class MemoryBlock:
    def __init__(self, start_at, memory_size, block_name):
        
        self.start_at = start_at
        self.memory_size = memory_size
        self.block_name = block_name
    
    def is_free(self):
        return self.block_name == "Free"

class MemoryAllocation:
    def __init__(self, pool_size, policy_name = None):
        
        self.pool_size = pool_size
        self.policy_name = policy_name
        self.blocks = [MemoryBlock(0, pool_size, "Free")]

    def choose_policy(self, policy_name):
        
        choosing = True
        
        while choosing:
            # A switch case for choosing a policy
            match policy_name:
            
                case "first-fit":
                    self.policy_name = policy_name
                    print(f"policy: {self.policy_name}")
                    return
            
                case "best-fit":
                    self.policy_name = policy_name
                    print(f"policy: {self.policy_name}")
                    return

                case "worst-fit":
                    self.policy_name = policy_name
                    print(f"policy: {self.policy_name}")
                    return

                case _:
                    print("Not a valid policy name")
                    policy_name = input("Choose a policy -> first-fit, best-fit, worst-fit: ")

    def search_block(self, memory_size):
        
        match self.policy_name:
            
            case "first-fit":
                return self.first_fit(memory_size)
            
            case "best-fit":
                return self.best_fit(memory_size)
            
            case "worst-fit":
                return self.worst_fit(memory_size)
        return None
    
    def free(self, block_name):
        
        is_found = False
        
        # Search for free block and merge adjacent memory block size
        for block in self.blocks:
            
            if block.block_name == block_name:
                
                is_found = True
                start_block = block.start_at 
                block.block_name = "Free"
                self.coalesce()
                
                # Combine as a whole block from beginning to the end
                for merge_block in self.blocks:
                    end_at = merge_block.start_at + merge_block.memory_size
                    
                    if merge_block.is_free() and merge_block.start_at <= start_block < end_at:
                        merge_block_at = merge_block.start_at
                        print(f"{block_name} freed (hole [{merge_block_at}-{end_at}) {merge_block.memory_size} bytes)")
                    
                        return
        
        if not is_found:
            print(f"Block cannot be found: {block_name}")

    def coalesce(self):
        
        index = 0
        
        while index < len(self.blocks) - 1:
            
            current = self.blocks[index]
            next_block = self.blocks[index + 1]

            if current.is_free() and next_block.is_free():
                
                current.memory_size += next_block.memory_size
                del self.blocks[index + 1]
            
            else:
                index += 1
    
    def get_used(self):
        
        used = 0

        for block in self.blocks:
            if not block.is_free():
                used += block.memory_size
        
        return used
    
    def get_free(self):
        
        free = 0

        for block in self.blocks:
            if block.is_free():
                free += block.memory_size
        
        return free
    
    def get_holes(self):
        
        holes = 0
        
        for block in self.blocks:
            if block.is_free():
                holes += 1

        return holes

    def get_largest(self):
        
        largest = 0

        for block in self.blocks:
            if block.is_free() and block.memory_size > largest:
                largest = block.memory_size

        return largest

    def stats(self):
        
        # Display stats
        used = self.get_used()
        free = self.get_free()
        holes = self.get_holes()
        largest = self.get_largest()
        frag = self.calculate_fragmentation()
        convert_frag = frag * 100

        print(f"pool: {self.pool_size}, used: {used}, free: {free}, holes: {holes}, largest hole: {largest}, fragmentation: {round(convert_frag, 1):.2f}%")

        free_blocks = []
        
        for block in self.blocks:
            if block.is_free():
                
                start = block.start_at
                end = block.start_at + block.memory_size
                
                free_blocks.append(f"[{start}-{end})")
        
        print("free list:", " ".join(free_blocks))

    def calculate_fragmentation(self):
        
        total_free = self.get_free()
        
        if total_free == 0:
            return 0
        
        largest_hole = self.get_largest()
        
        frag = 1 - (largest_hole / total_free)
        
        return frag 
            
    def allocate(self, memory_size, block_name):
        
        for block in self.blocks:
            
            if block.block_name == block_name:
                print(f"You enter a duplicate block name {block_name}.")
                return
        
        # Find a block of memory to allocate based on policy
        block = self.search_block(memory_size)
        
        start_at = block.start_at

        if block.memory_size == memory_size:
            block.block_name = block_name
        
        # Calculate memory size
        else:
            
            remaining_block_size = block.memory_size - memory_size
            allocated_block = MemoryBlock(start_at, memory_size, block_name)
            free_block = MemoryBlock(start_at + memory_size, remaining_block_size, "Free")

            index = self.blocks.index(block)
            self.blocks[index: index + 1] = [allocated_block, free_block]

        print(f"{block_name}: {memory_size} bytes at [{start_at}-{start_at + memory_size})")

    def first_fit(self, memory_size):
        
        for block in self.blocks:
            if block.is_free() and block.memory_size >= memory_size:
                return block
        
        return None

    def best_fit(self, memory_size):
        
        best = None
        
        for block in self.blocks:
            
            if block.is_free() and block.memory_size >= memory_size:
                if best is None or block.memory_size < best.memory_size:
                    best = block
        
        return best

    def worst_fit(self, memory_size):
        
        worst = None
        
        for block in self.blocks:
            
            if block.is_free() and block.memory_size >= memory_size:
                if worst is None or block.memory_size > worst.memory_size:
                    worst = block
        
        return worst

def run():

    starting_allocation = 0
    free_block = "Free"
    allocator = MemoryAllocation(0)
    policy = input("Enter policy: ")
    
    allocator.choose_policy(policy)
    pool_size = int(input("Enter memory pool size: "))
    allocator.pool_size = pool_size
    allocator.blocks = [MemoryBlock(starting_allocation, pool_size, free_block)]
    
    running = True
    
    while running:
        
        command = input("alloc> ").split()
        if not command:
            continue

        # Switch case -> On command line
        match command[0]:
            case "policy":
                allocator.choose_policy(command[1])
            
            case "alloc":
                allocator.allocate(int(command[2]), command[1])
            
            case "free":
                allocator.free(command[1])
            
            case "stats":
                allocator.stats()
            
            case "exit":
                break
            
            case _:
                print("Not a command.")

if __name__ == "__main__":
    run()