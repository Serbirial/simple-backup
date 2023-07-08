def insert_imports(_imports: dict) -> None:
    global imports
    imports = _imports
# Any main data you need will be inserted into imports through this function. Dont remove the code above. Dont modify it.
# If you do, know the source code already and know how the entire project works.

def compression_replacement(parent, paths):
    print(parent)     # The folder you are given to compress
    print(paths)      # Paths to all the files in the folder you have been given to compress.
    print(imports)    # All the data the internal compression function you replaced would use. 
    print(some_internal_function())
    return len(paths) # You are expected to return the ammount of files that you compressed.
                      # Its preferred you add to a counter for every file to keep track.

def some_internal_function(): # You can internally declare and use functions.
    return "Some data or something"

exports = {
    "name": "Test Addon", # The name of your addon.
    "replaces": {"compress": compression_replacement}, # The function it replaces, check backup/addons.py for a list of replacable functions and explanations
}




# NOTE: DO NOT ATTEMPT TO IMPORT ANY ORIGINAL FILES TO REPLACE FUNCTIONS, YOU CANNOT ACTUALLY MODIFY INTERNAL FUNCTIONS.
# IF YOU DO, I WILL NOT PROVIDE ANY SUPPORT AT ALL
# YOUR FUNCTIONS ARE NOT ACTUALLY REPLACING THE INTERNAL ONES.