import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import sqlite3
import os

class LandAcquisitionBlock:
    """
    Represents a single block in the land acquisition blockchain.
    Each block contains multiple transactions related to land acquisition activities.
    """
    
    def __init__(self, index: int, transactions: List[Dict], previous_hash: str, timestamp: float = None):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = self._calculate_merkle_root()
        self.nonce = 0
        self.hash = self._calculate_hash()
    
    def _calculate_merkle_root(self) -> str:
        """Calculate Merkle root of all transactions in the block."""
        if not self.transactions:
            return hashlib.sha256(b'').hexdigest()
        
        tx_hashes = [hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest() 
                    for tx in self.transactions]
        
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 == 1:
                tx_hashes.append(tx_hashes[-1])
            
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            
            tx_hashes = new_hashes
        
        return tx_hashes[0]
    
    def _calculate_hash(self) -> str:
        """Calculate the hash of the block."""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 4):
        """Mine the block with proof of work."""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self._calculate_hash()
        
        print(f"Block mined: {self.hash}")

class LandAcquisitionBlockchain:
    """
    Main blockchain class for managing land acquisition records.
    Provides immutable ledger functionality for all land acquisition activities.
    """
    
    def __init__(self, db_path: str = "land_acquisition.db"):
        self.chain: List[LandAcquisitionBlock] = []
        self.pending_transactions: List[Dict] = []
        self.mining_reward = 0  # No mining reward for government system
        self.difficulty = 2  # Low difficulty for faster processing
        self.db_path = db_path
        self._init_database()
        self._load_blockchain_from_db()
        
        if len(self.chain) == 0:
            self._create_genesis_block()
    
    def _init_database(self):
        """Initialize SQLite database for blockchain persistence."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_index INTEGER UNIQUE,
                timestamp REAL,
                transactions TEXT,
                previous_hash TEXT,
                merkle_root TEXT,
                nonce INTEGER,
                hash TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT,
                block_index INTEGER,
                transaction_type TEXT,
                survey_number TEXT,
                village TEXT,
                tehsil TEXT,
                timestamp REAL,
                FOREIGN KEY (block_index) REFERENCES blocks (block_index)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_blockchain_from_db(self):
        """Load existing blockchain from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM blocks ORDER BY block_index')
        rows = cursor.fetchall()
        
        for row in rows:
            _, block_index, timestamp, transactions_json, previous_hash, merkle_root, nonce, block_hash = row
            transactions = json.loads(transactions_json)
            
            block = LandAcquisitionBlock(block_index, transactions, previous_hash, timestamp)
            block.merkle_root = merkle_root
            block.nonce = nonce
            block.hash = block_hash
            
            self.chain.append(block)
        
        conn.close()
    
    def _save_block_to_db(self, block: LandAcquisitionBlock):
        """Save a block to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO blocks 
            (block_index, timestamp, transactions, previous_hash, merkle_root, nonce, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            block.index,
            block.timestamp,
            json.dumps(block.transactions),
            block.previous_hash,
            block.merkle_root,
            block.nonce,
            block.hash
        ))
        
        # Index transactions for quick searching
        for tx in block.transactions:
            cursor.execute('''
                INSERT INTO transaction_index 
                (transaction_id, block_index, transaction_type, survey_number, village, tehsil, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                tx.get('transaction_id', ''),
                block.index,
                tx.get('type', ''),
                tx.get('survey_number', ''),
                tx.get('village', ''),
                tx.get('tehsil', ''),
                tx.get('timestamp', block.timestamp)
            ))
        
        conn.commit()
        conn.close()
    
    def _create_genesis_block(self):
        """Create the first block in the blockchain."""
        genesis_transactions = [{
            'transaction_id': 'GENESIS',
            'type': 'SYSTEM_INIT',
            'timestamp': time.time(),
            'data': {
                'message': 'Land Acquisition Blockchain System Initialized',
                'version': '1.0.0',
                'created_by': 'Government Land Acquisition Department'
            }
        }]
        
        genesis_block = LandAcquisitionBlock(0, genesis_transactions, "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        self._save_block_to_db(genesis_block)
    
    def get_latest_block(self) -> LandAcquisitionBlock:
        """Get the latest block in the chain."""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Dict) -> str:
        """Add a new transaction to pending transactions."""
        transaction_id = hashlib.sha256(
            (json.dumps(transaction, sort_keys=True) + str(time.time())).encode()
        ).hexdigest()
        
        transaction['transaction_id'] = transaction_id
        transaction['timestamp'] = time.time()
        
        self.pending_transactions.append(transaction)
        return transaction_id
    
    def mine_pending_transactions(self) -> bool:
        """Mine all pending transactions into a new block."""
        if not self.pending_transactions:
            return False
        
        block = LandAcquisitionBlock(
            len(self.chain),
            self.pending_transactions.copy(),
            self.get_latest_block().hash
        )
        
        block.mine_block(self.difficulty)
        self.chain.append(block)
        self._save_block_to_db(block)
        
        self.pending_transactions = []
        return True
    
    def create_award_declaration(self, project_name: str, survey_numbers: List[str], 
                               village: str, tehsil: str, district: str, 
                               compensation_rate: float, officer_id: str) -> str:
        """Create an award declaration transaction."""
        transaction = {
            'type': 'AWARD_DECLARATION',
            'project_name': project_name,
            'survey_numbers': survey_numbers,
            'village': village,
            'tehsil': tehsil,
            'district': district,
            'compensation_rate': compensation_rate,
            'officer_id': officer_id,
            'status': 'DECLARED'
        }
        return self.add_transaction(transaction)
    
    def create_compensation_payment(self, survey_number: str, property_number: str,
                                  beneficiary_name: str, beneficiary_account: str,
                                  amount: float, payment_method: str, 
                                  officer_id: str) -> str:
        """Create a compensation payment transaction."""
        transaction = {
            'type': 'COMPENSATION_PAYMENT',
            'survey_number': survey_number,
            'property_number': property_number,
            'beneficiary_name': beneficiary_name,
            'beneficiary_account': beneficiary_account,
            'amount': amount,
            'payment_method': payment_method,
            'officer_id': officer_id,
            'status': 'PAID'
        }
        return self.add_transaction(transaction)
    
    def create_query_record(self, survey_number: str, query_type: str,
                          complainant_name: str, query_details: str,
                          officer_id: str) -> str:
        """Create a citizen query/complaint record."""
        transaction = {
            'type': 'CITIZEN_QUERY',
            'survey_number': survey_number,
            'query_type': query_type,
            'complainant_name': complainant_name,
            'query_details': query_details,
            'officer_id': officer_id,
            'status': 'RECEIVED'
        }
        return self.add_transaction(transaction)
    
    def create_litigation_record(self, survey_number: str, case_number: str,
                               court_name: str, case_details: str,
                               officer_id: str) -> str:
        """Create a litigation record."""
        transaction = {
            'type': 'LITIGATION',
            'survey_number': survey_number,
            'case_number': case_number,
            'court_name': court_name,
            'case_details': case_details,
            'officer_id': officer_id,
            'status': 'UNDER_LITIGATION'
        }
        return self.add_transaction(transaction)
    
    def get_transactions_by_survey_number(self, survey_number: str) -> List[Dict]:
        """Get all transactions for a specific survey number."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT b.transactions FROM blocks b
            JOIN transaction_index ti ON b.block_index = ti.block_index
            WHERE ti.survey_number = ?
            ORDER BY b.timestamp
        ''', (survey_number,))
        
        results = []
        for row in cursor.fetchall():
            transactions = json.loads(row[0])
            for tx in transactions:
                if tx.get('survey_number') == survey_number:
                    results.append(tx)
        
        conn.close()
        return results
    
    def get_transactions_by_village(self, village: str) -> List[Dict]:
        """Get all transactions for a specific village."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT b.transactions FROM blocks b
            JOIN transaction_index ti ON b.block_index = ti.block_index
            WHERE ti.village = ?
            ORDER BY b.timestamp
        ''', (village,))
        
        results = []
        for row in cursor.fetchall():
            transactions = json.loads(row[0])
            for tx in transactions:
                if tx.get('village') == village:
                    results.append(tx)
        
        conn.close()
        return results
    
    def validate_chain(self) -> bool:
        """Validate the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != current_block._calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_blockchain_stats(self) -> Dict:
        """Get blockchain statistics."""
        total_blocks = len(self.chain)
        total_transactions = sum(len(block.transactions) for block in self.chain)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT transaction_type, COUNT(*) FROM transaction_index GROUP BY transaction_type")
        transaction_types = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_blocks': total_blocks,
            'total_transactions': total_transactions,
            'pending_transactions': len(self.pending_transactions),
            'transaction_types': transaction_types,
            'is_valid': self.validate_chain()
        }

# Initialize global blockchain instance
land_blockchain = LandAcquisitionBlockchain()