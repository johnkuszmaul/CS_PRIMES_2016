import linear_pebble
import pebbling_algos
import utils
import random # is this the right random number generator to use?

# trees.py is no longer used anywher in the code.

##### PRIMITIVE PROVER/VERIFIER SETUP #####
# Prover pebbles PTC graph, generates Merkle tree, and sends root to Verifier
# Verifier has Prover open n randomly chosen leaves of the MT, where n is
# 	defined in terms of r (currently it is set to n = 30, as recommended in SpaceMint and by Ling)
# In each opening, Prover sends over an Opening object containing the leaf value
# 	and the sibling path.  Verifier then uses the Opening to recalculate the
# 	Merkle root, and compares it against the original one sent by Prover.
# If Prover passes all n test cases, then Verifier.verify() outputs True; other-
# 	wise, it outputs False.
#
# Note: in this version, Prover is completely honest (i.e. uses trivial_pebble)
# 	and stores the value of every PTC vertex using i/o file storage), Verifier does not
# 	actually send over the sources, nor does he specifically check for the vali-
#	dity of some fixed number of sources.

class Prover:
        def __init__(self, r, pre_gen_graph=False, debug=False):
                self.debug = debug
                if self.debug:
                        print "P: Starting up."
                self.r = r
		self.p = linear_pebble.PebbleGraph(r, pre_generated_graph=pre_gen_graph)
                pebbling_algos.linear_trivial_pebble(self.p)

                self.merkle_tree_rows = 1
                while(2**(self.merkle_tree_rows - 1) < self.p.size):
                        self.merkle_tree_rows += 1
                self.merkle_tree_size = 2**(self.merkle_tree_rows) - 2 # This is actually one less than the size. It actually stands for the number of the last node numbered 0 - n.

                # Finishes filling bottom row of merkle tree.
                self.p.pebble_value.seek(self.p.size * self.p.hash_length)
                for i in range(2**(self.merkle_tree_rows-1) - self.p.size):
		    self.p.pebble_value.write("\00" * self.p.hash_length)
                self.merkle_root = ""

		if self.debug:
			print "P: Good to go, __init__ completed."

        def create_merkle_tree(self):
                # Creates merkle tree
                vertex = 2**(self.merkle_tree_rows - 1) - 2
                while vertex >= 0:
                        self.p.pebble_value.seek((self.merkle_tree_size - (2*vertex + 2)) * self.p.hash_length)
                        prehash = self.p.pebble_value.read(2 * self.p.hash_length) # reads both hash values at once!
                        self.p.pebble_value.seek((self.merkle_tree_size - vertex) * self.p.hash_length)
                        self.p.pebble_value.write(utils.secure_hash(prehash))
                        vertex -= 1

                # Finds merkle root
                self.p.pebble_value.seek(self.merkle_tree_size * self.p.hash_length)
                self.merkle_root = self.p.pebble_value.read(self.p.hash_length)
                
                        
	def send_root(self):
		if self.debug:
			print "P: Sending over my Merkle root: "+self.merkle_root # "" is the key of the root, and [0] returns its value
		return self.merkle_root


	def close_files(self):
		if self.debug:
			print "P: Closing all my files.  Good night."
		self.p.close_files()

class Verifier:
	# rroot is the received root from the prover -- verifier doesn't know for sure if the root is legitimate

	def __init__(self, r, debug=False):
		self.debug = debug
		if self.debug:
			print "V: Initializing."
		self.r = r
		self.n = 30 # n is the number of vertices that the Verifier is going to open
		if self.debug:
			print "V: Initialization complete."

	def set_prover(self, prover):
		self.prover = prover
		if self.debug:
			print "V: Prover set."
                        
	def verify(self):
		if self.debug:
			print "V: Time to verify.  I will be checking "+str(self.n)+" randomly chosen vertices."
		self.receive_root()
		for x in range(self.n):
			i = self.choose_vertex()
			if self.debug:
				print "V: Verification trial #"+str(x+1)+" -- vertex index "+str(i)+"."
			result = self.verify_opening(i)
                        if result == False:
                                return False
		return True

	def choose_vertex(self):
		return int(self.prover.p.size * random.random())

	def receive_root(self):
		self.rroot = self.prover.send_root()
		if self.debug:
			print "V: Got your root."

        # Verifies opening node i in the PTC graph.
	def verify_opening(self, i): # returns True for pass, False for fail
                node_number = self.prover.merkle_tree_size - i
                self.prover.p.pebble_value.seek(i *  self.prover.p.hash_length)
                hash_of_node = self.prover.p.pebble_value.read(self.prover.p.hash_length)

                row = self.prover.merkle_tree_rows
                while (row > 1):
                        if node_number % 2 == 0: # Node has a sibling to the right
                                self.prover.p.pebble_value.seek((self.prover.merkle_tree_size - (node_number - 1)) * self.prover.p.hash_length)
                                sibling = self.prover.p.pebble_value.read(self.prover.p.hash_length)
                                node_number = node_number/2 - 1
                                hash_of_node = utils.secure_hash(hash_of_node + sibling)
                        else: # Node has a sibling to the left.
                                self.prover.p.pebble_value.seek((self.prover.merkle_tree_size - (node_number + 1)) * self.prover.p.hash_length)
                                sibling = self.prover.p.pebble_value.read(self.prover.p.hash_length)
                                node_number = node_number/2
                                hash_of_node = utils.secure_hash(sibling + hash_of_node)
                                
                        row = row - 1

                if hash_of_node == self.prover.merkle_root:
                        return True
                else:
                        return False

