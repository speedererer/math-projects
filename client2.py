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


def client_program():
    host = '192.168.106.138'
    port = 12000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server


    char_key="4"
    message="confirm connection"
    client_socket.send(message.encode())
    data = client_socket.recv(1024).decode()  # receive response

    print('Received from server: ' + data)

    while message.lower().strip() != 'bye':





        plain_text = input(" -> ") # again take input
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
        message=cipher_string

        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response
        cipher_text= data

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
        print('Received from server: ' + data+' '+ '\ndecoded:'+ plain_text)  # show in terminal


    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()