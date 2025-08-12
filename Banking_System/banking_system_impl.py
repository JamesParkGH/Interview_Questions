from banking_system import BankingSystem
from collections import defaultdict, deque
import math

CASHBACK_DELAY = 86400000  # 24 hours in milliseconds

class BankingSystemImpl(BankingSystem):
    def __init__(self):
        self.accounts = {}  # account_id -> balance
        self.outgoing = defaultdict(int)  # account_id -> total outgoing
        self.history = defaultdict(list)  # account_id -> [(timestamp, balance)]
        self.payments = {}  # payment_id -> (account_id, timestamp, amount, status)
        self.pending_cashbacks = []  # (timestamp_to_refund, account_id, amount, payment_id)
        self.payment_counter = 0
        self.merged = {}  # old_id -> new_id (for merged accounts)
        self.payment_lookup = defaultdict(dict)  # account_id -> {payment_id -> actual_id}

    def _get_actual_id(self, account_id):
        while account_id in self.merged:
            account_id = self.merged[account_id]
        return account_id

    def _record_history(self, account_id, timestamp):
        balance = self.accounts[account_id]
        self.history[account_id].append((timestamp, balance))

    def _process_cashbacks(self, timestamp):
        new_pending = []
        for refund_time, acct, amt, pay_id in self.pending_cashbacks:
            acct = self._get_actual_id(acct)
            if refund_time <= timestamp:
                if acct in self.accounts:
                    self.accounts[acct] += amt
                    self._record_history(acct, refund_time)
                    if pay_id in self.payments:
                        self.payments[pay_id] = (acct, refund_time, amt, "CASHBACK_RECEIVED")
            else:
                new_pending.append((refund_time, acct, amt, pay_id))
        self.pending_cashbacks = new_pending

    def create_account(self, timestamp, account_id):
        account_id = self._get_actual_id(account_id)
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = 0
        self._record_history(account_id, timestamp)
        return True

    def deposit(self, timestamp, account_id, amount):
        self._process_cashbacks(timestamp)
        account_id = self._get_actual_id(account_id)
        if account_id not in self.accounts:
            return None
        self.accounts[account_id] += amount
        self._record_history(account_id, timestamp)
        return self.accounts[account_id]

    def transfer(self, timestamp, source_id, target_id, amount):
        self._process_cashbacks(timestamp)
        source_id = self._get_actual_id(source_id)
        target_id = self._get_actual_id(target_id)
        if source_id == target_id or source_id not in self.accounts or target_id not in self.accounts:
            return None
        if self.accounts[source_id] < amount:
            return None
        self.accounts[source_id] -= amount
        self.accounts[target_id] += amount
        self.outgoing[source_id] += amount
        self._record_history(source_id, timestamp)
        self._record_history(target_id, timestamp)
        return self.accounts[source_id]

    def pay(self, timestamp, account_id, amount):
        self._process_cashbacks(timestamp)
        account_id = self._get_actual_id(account_id)
        if account_id not in self.accounts or self.accounts[account_id] < amount:
            return None
        self.accounts[account_id] -= amount
        self._record_history(account_id, timestamp)
        self.outgoing[account_id] += amount

        cashback = amount * 2 // 100  # 2% cashback rounded down
        cashback_time = timestamp + CASHBACK_DELAY
        self.payment_counter += 1
        payment_id = f"payment{self.payment_counter}"
        self.payments[payment_id] = (account_id, timestamp, amount, "IN_PROGRESS")
        self.pending_cashbacks.append((cashback_time, account_id, cashback, payment_id))
        self.payment_lookup[account_id][payment_id] = payment_id
        return payment_id

    def get_payment_status(self, timestamp, account_id, payment_id):
        self._process_cashbacks(timestamp)
        actual_id = self._get_actual_id(account_id)
        if actual_id not in self.accounts:
            return None
        actual_payment = self.payment_lookup.get(actual_id, {}).get(payment_id, payment_id)
        if actual_payment not in self.payments:
            return None
        payment_owner, _, _, status = self.payments[actual_payment]
        if self._get_actual_id(payment_owner) != actual_id:
            return None
        return status

    def top_spenders(self, timestamp, n):
        self._process_cashbacks(timestamp)
        spenders = []
        for acc_id in self.accounts:
            real_id = self._get_actual_id(acc_id)
            if real_id != acc_id:
                continue  # skip merged-away accounts
            total = self.outgoing.get(real_id, 0)
            spenders.append((real_id, total))
        # sort: descending by amount, ascending by account_id
        spenders.sort(key=lambda x: (-x[1], x[0]))
        result = []
        for i in range(min(n, len(spenders))):
            acc, amt = spenders[i]
            result.append(f"{acc}({amt})")
        return result

    def merge_accounts(self, timestamp, id1, id2):
        self._process_cashbacks(timestamp)
        id1 = self._get_actual_id(id1)
        id2 = self._get_actual_id(id2)
        if id1 == id2 or id1 not in self.accounts or id2 not in self.accounts:
            return False

        # Merge balances
        self.accounts[id1] += self.accounts[id2]
        self._record_history(id1, timestamp)

        # Merge outgoing totals
        self.outgoing[id1] += self.outgoing[id2]

        # Redirect history
        for ts, bal in self.history[id2]:
            self.history[id1].append((ts, bal))
        self.history[id1].sort()

        # Update merged map
        self.merged[id2] = id1

        # Transfer payment mappings
        for pid in self.payment_lookup.get(id2, {}):
            self.payment_lookup[id1][pid] = pid

        # Cleanup
        del self.accounts[id2]
        if id2 in self.outgoing:
            del self.outgoing[id2]
        if id2 in self.history:
            del self.history[id2]
        if id2 in self.payment_lookup:
            del self.payment_lookup[id2]
        return True

    def get_balance(self, timestamp, account_id, time_at):
        self._process_cashbacks(timestamp)
        account_id = self._get_actual_id(account_id)
        if account_id not in self.history:
            return None
        balance_at = None
        for ts, bal in self.history[account_id]:
            if ts <= time_at:
                balance_at = bal
            else:
                break
        return balance_at
