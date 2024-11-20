class HeapMemoryManager:
    def __init__(self, start_address=10304, size=1024):
        self.start_address = start_address  # Starting from 10304 (after stack segment)
        self.size = size
        self.blocks = [(start_address, size, None)]  # (start_address, size, in_use)
        
    def first_fit(self, required_size):
        for i, (start, size, in_use) in enumerate(self.blocks):
            if not in_use and size >= required_size:
                # Split the block if it's larger than needed
                if size > required_size:
                    self.blocks[i] = (start, required_size, True)
                    self.blocks.insert(i + 1, (start + required_size, size - required_size, None))
                else:
                    self.blocks[i] = (start, size, True)
                return start
        return None

    def deallocate(self, address):
        for i, (start, size, in_use) in enumerate(self.blocks):
            if start == address:
                self.blocks[i] = (start, size, None)
                # Merge with next block if it's free
                if i + 1 < len(self.blocks) and not self.blocks[i + 1][2]:
                    next_start, next_size, _ = self.blocks[i + 1]
                    self.blocks[i] = (start, size + next_size, None)
                    self.blocks.pop(i + 1)
                # Merge with previous block if it's free
                if i > 0 and not self.blocks[i - 1][2]:
                    prev_start, prev_size, _ = self.blocks[i - 1]
                    self.blocks[i - 1] = (prev_start, prev_size + size, None)
                    self.blocks.pop(i)
                return True
        return False
