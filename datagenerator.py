import numpy as np
import argparse
from pathlib import Path

"""
Data generator for the MiniZinc environment (.dnz files),
capable of generating literal matrices, matrices of disjunct literals, 
balanced matrices and at most one restrictions.

Execution:
For executing the programs need to be provided of the following data:
Mandatory:
@:param t: Max number of literals
@:param k:, Maximum size of support set"
@:param n: Number of positive instances
@:param m: Number of negative instances
@:param c: Number of atMostOne Constraints

Optional:

@:param b: bias value for biasing the value of the literals (0 .. 1)
@:param o: Output file(s) name, filename(s) will result as filename1, filename2...")
@:param p: Directory path of the generated files
@:param n: Number of test files
"""


def generate_data_set(args):
    """
    Generates the .dnz data files
    :param args: given at the script execution [t, k, n, m, c,, b, o , p , n]
    :return: .dnz data set files
    """
    if args.o is None:
        filename = "test"
    else:
        filename = args.o

    if args.b is None:
        args.b = 0.5
    if args.p is None:
        path = Path("")
    else:
        path =Path("source_data/text_files/")
    if args.nf is None:
        args.nf = 1

    for i in range(int(args.nf)):
        args.o = path / (filename + str(i) + ".dnz")
        create_dnz_file(args)



def create_dnz_file(args):
    """
    Creates the .dnz file with the randomized data
    :param args: given at the script execution [t, k, n, m, c,, b, o , p , n]
    :return: .dnz formatted file with randomized data
    """

    file = open(args.o, 'w')

    file.write("% ----DATA VARIABLES----\n\n")
    file.write("t=" + str(args.t) + ";" + "%number of attributes\n")
    file.write("n=" + str(args.n) + ";" + "%number of positive instances\n")
    file.write("m=" + str(args.m) + ";" + "%number of negative instances\n")
    file.write("c=" + str(args.c) + ";" + "%number of atMostOne Constraints\n\n")

    file.write("% ----OMEGAS----\n\n")

    omega_p = generate_omega_data(args.t, args.n, args.b)
    file.write("omegap= " + omega_to_mz(omega_p) + "\n\n")

    omega_n = generate_disjoint_omega_data(omega_p, args.m, args.b)
    file.write("omegan= " + omega_to_mz(omega_n) + "\n\n")

    file.write("% ----CONSTRAINS----\n\n")
    at_most_one = generate_at_most_one(int(args.t/2), args.c, 1, args.t)
    file.write("atMostOne=" + at_most_one_to_mz(at_most_one))

def generate_omega_data(*args):

    """
    Choose between the different omega generation functions
    :param args: number of literals, number of columns, bias factor
    :return: matrix of literals
    """
    if len(args) == 2:
        return generate_omega(args[0], args[1])
    else:
        return generate_biased_omega(args[0], args[1], args[2])


def generate_disjoint_omega_data(*args):
    """
    Generate a matrix of random literals
    :param args: number of literals, number of columns, bias factor
    :return: a matrix disjoint to the one provided
    """
    if len(args) == 2:
        return generate_disjoint_omega(args[0], args[1])
    else:
        return generate_disjoint_biased_omega(args[0], args[1], args[2])


def generate_omega(num_literals, num_columns):
    """
    Generate a matrix of random literals
    :param num_literals: max number of literals
    :param num_columns: max number of columns
    :return: matrix of literals
    """
    omega = []
    for i in range(num_columns):
        omega.append(generate_random_literals(num_literals, 0, 2))

    return omega


def generate_biased_omega(num_literals, num_columns, bias):
    """
    :param num_literals: max number of literals
    :param num_columns: max number of columns
    :param bias: bias factor for balancing literal values
    :return: matrix of literals
    """
    omega = []
    for i in range(num_columns):
        omega.append(generate_random_biased_literals(num_literals, bias))

    return omega


def generate_disjoint_omega(omega, num_columns):
    """
    Generates a disjoint matrix to the one provided
    :param omega: matrix to apply the disjunction
    :param num_columns: max number of columns of the disjoint matrix
    :return: disjoint matrix
    """
    dis_omega = []
    while len(dis_omega) != num_columns:
        lit_set = generate_random_literals(len(omega[1]), 0, 2)
        if check_disjunction(omega, lit_set):
            dis_omega.append(lit_set)

    return dis_omega


def generate_disjoint_biased_omega(omega, num_columns, bias):
    """
    Generates a disjoint matrix to the one provided with biased literal values
    :param omega: matrix to apply the disjunction
    :param num_columns: max number of columns
    :param bias: bias factor for balancing literal values
    :return: disjoint matrix
    """
    dis_omega = []
    while len(dis_omega) != num_columns:
        lit_set = generate_random_biased_literals(len(omega[1]), bias)
        if check_disjunction(omega, lit_set):
            dis_omega.append(lit_set)

    return dis_omega


def check_disjunction(omega, lit_set):
    for i in range(len(omega)):
        if omega[i] == lit_set:
            return False
        elif omega[i] != lit_set and i == (len(omega) - 1):
            return True


def generate_random_literals(num_literals, min_value, max_value):

    return list(map(lambda lit: np.random.randint(min_value, max_value), range(num_literals)))


def generate_random_biased_literals(num_literals, bias):
    lit_set = []
    for i in range(num_literals):
        if np.random.uniform(0, 1) > bias:
            lit_set.append(1)
        else:
            lit_set.append(0)
    return lit_set

def generate_at_most_one (max_literals, num_columns, min_lit_value, max_lit_value):
    at_most_one = []
    for i in range(num_columns):
        at_most_one.append(generate_random_literals(np.random.randint(1, max_literals), min_lit_value, max_lit_value))

    return at_most_one


def omega_to_mz(omega):
    omega_mz = ""
    for line in omega:
        omega_mz += str(line) + "\n"
    omega_mz = omega_mz.replace('[', " ")
    omega_mz = "[|" + omega_mz.replace(']', '|') + "];"
    return omega_mz


def at_most_one_to_mz(at_most_one):
    at_most_one_mz = str(at_most_one)
    at_most_one_mz = at_most_one_mz[:-1].replace('[', '{')
    at_most_one_mz = at_most_one_mz[1:].replace(']', '}')
    return "[" + at_most_one_mz + "];"


def get_arguments():

    parser = argparse.ArgumentParser(description="MiniZinc data generator")
    parser.add_argument("-t", help="Max number of literals", type=int, required=True)
    parser.add_argument("-k", help="Maximum size of support set", type=int, required=True)
    parser.add_argument("-n", help="Number of positive instances", type=int, required=True)
    parser.add_argument("-m", help="Number of negative instances", type=int, required=True)
    parser.add_argument("-c", help="Number of atMostOne Constraints", type=int, required=True)
    parser.add_argument("--b", help="bias value for biasing the value of the literals (0 .. 1)")
    parser.add_argument("-o", help="Output file(s) name, filename(s) will result as filename1, filename2...")
    parser.add_argument("-p", help="Directory path of the generated files")
    parser.add_argument("-nf", help="Number of test files", type=int)

    return parser.parse_args()
