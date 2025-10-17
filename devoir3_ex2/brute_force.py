#!/usr/bin/env python3

import time
import secrets
from mini_chacha import MiniChaCha

def brute_force():
    chanson = "Une souris verte qui courait dans l'herbe".encode("utf-8")
    nom = "JEDD"
    
    # Create cipher with a random key
    true_cipher = MiniChaCha(nom)
    true_key = true_cipher.key4
    nonce = true_cipher.nonce2
    
    print(f"True key: {true_key.hex()}")
    print(f"Nonce: {nonce.hex()}")
    print(f"Chanson: {chanson.decode()}")
    
    # Encrypt with true cipher
    true_cypherchanson = true_cipher.encrypt(chanson)
    print(f"Result: {true_cypherchanson.hex()}")
    
    print("\n ## Start brute force")
    
    start_time = time.time()
    tries = 0
    max_tries = 1000000
    
    for key_int in range(max_tries):
        # Generate sequential key
        test_key = key_int.to_bytes(4, 'little')
        
        # Create cipher with test key
        test_cipher = MiniChaCha(nom, key4=test_key, nonce2=nonce, counter_start=1)
        test_cipherchanson = test_cipher.encrypt(chanson)
        tries += 1
        
        # Compare
        if test_cipherchanson == true_cypherchanson:
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            print(f"\n Key found!")
            print(f"Key: {test_key.hex()}")
            print(f"Tries: {tries:,}")
            print(f"Time: {elapsed_time:.2f} seconds")
            
            # check chanson
            chanson_result = test_cipher.decrypt(test_cipherchanson)
            print(f"Chanson: {chanson_result.decode()}")
            
            return tries, elapsed_time
    
    # Key not found
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("\n Key not found")
    print(f"Total time: {elapsed_time:.2f} seconds")
    
    return None, elapsed_time


if __name__ == "__main__":
    # Ex2: part 4
    result = brute_force()
    
    if result[0] is not None:
        tries, elapsed_time = result
        print(f"\nResult: Key found in {tries:,} tries over {elapsed_time:.2f} seconds.")