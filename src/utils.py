# Reserved for helper functions (chunking, cleaning, etc.)

def chunk_list(lst, n):
    "Yield n-sized chunks from list."
    for i in range(0, len(lst), n):
        yield lst[i:i+n]