import socket
import networkx as nx
import numpy as np
import math

def generating_matrix_key(order):
    """
    This function generates a square matrix key of a particular pattern of order 'order'.
    :param order: int. Order of the square matrix key.
    :return: Returns a nested list of the matrix key
    """
    key = []
    for r in range(0, order):
        key_row = []
        for c in range(0, order):
            if r <= c:
                key_row.append(order - r)
            else:
                key_row.append(order - c)
        key.append(key_row)
    return key

def matrix_multiplication(matrix_a, matrix_b, order):
    """
    This function multiplies two square matrices of the same order in the sequence of the matrices entered.
    :param matrix_a: Nested list. First square matrix of order 'order'.
    :param matrix_b: Nested list. Second square matrix of order 'order'.
    :param order: int. Order of the square matrices.
    :return: Returns a nested list of the product of 'matrix_a' and 'matrix_b'.
    """
    product_matrix = []
    for x in range(0, order):
        product_row = []
        for y in range(0, order):
            product_sum = 0
            for z in range(0, order):
                product_sum += matrix_a[x][z] * matrix_b[z][y]
            product_row.append(product_sum)
        product_matrix.append(product_row)
    return product_matrix


# Creating a list of all possible ascii inputs
ascii_char = [chr(i) for i in range(32, 127)]



def server_program():
    # get the hostname
    host = "192.168.106.42"
    port = 12000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(10)
    conn, address = server_socket.accept() # accept new connection
    char_key="4"
    print("Connection from: " + str(address))
    message = "confirm connection"
    conn.send(message.encode())

    data=conn.recv(1024).decode()
    print("from connected user: " + str(data))
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        cipher_text = data

        # Creating the cipher matrix from the cipher text
        cipher_list = list(map(int, cipher_text.split(" ")))
        n = int(math.sqrt(len(cipher_list)))
        cipher_matrix = np.array(cipher_list).reshape(n, n).tolist()

        # Generating an invertible matrix key
        matrix_key = generating_matrix_key(order=n)

        # Finding the inverse of matrix key
        matrix_key_inverse = np.linalg.inv((np.array(matrix_key)))

        # Multiplying inverse of matrix key to cipher matrix to get back adjacency matrix
        adjacency_matrix = matrix_multiplication(matrix_a=cipher_matrix, matrix_b=matrix_key_inverse, order=n)

        # Decrypting the adjacency matrix to plain text
        decrypted_text = char_key
        for i in range(0, n - 1):
            decrypted_text += ascii_char[ascii_char.index(decrypted_text[i]) + int(adjacency_matrix[i][i + 1])]
        plain_text = decrypted_text[1:]
        if not data:
            # if data is not received break
            break
        print("from connected user: " + str(data)+' '+ 'decoded:'+ plain_text)
        plain_text = input(" -> ")  # again take input
        plain_text = char_key + plain_text
        n = len(plain_text)

        # Generating an invertible matrix key
        matrix_key = generating_matrix_key(order=n)

        # Creating a graph with special character key
        G = nx.Graph()
        for i in range(0, n - 1):
            G.add_edge(i, i + 1, weight=(ascii_char.index(plain_text[i + 1]) - ascii_char.index(plain_text[i])))

        # Creating adjacency matrix of the graph
        adjacency_matrix = nx.adjacency_matrix(G).todense().tolist()

        # Creating the cipher matrix by multiplying adjacency matrix and matrix key
        cipher_matrix = matrix_multiplication(matrix_a=adjacency_matrix, matrix_b=matrix_key, order=n)

        # Printing cipher text
        cipher_string = ""
        for i in range(0, n):
            for j in range(0, n):
                cipher_string += f"{cipher_matrix[i][j]} "
        cipher_string = cipher_string.rstrip(" ")
        data = cipher_string

        conn.send(data.encode())  # send data to the client

    conn.close()  # close the connection


if __name__ == '__main__':
    server_program()