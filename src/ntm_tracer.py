import os
from src.helpers.turing_machine import TuringMachineSimulator, BLANK


# ==========================================
# PROGRAM 1: Nondeterministic TM [cite: 137]
# ==========================================
class NTM_Tracer(TuringMachineSimulator):
    def run(self, input_string, max_depth):
        """
        Performs a Breadth-First Search (BFS) trace of the NTM.
        Ref: Section 4.1 "Trees as List of Lists" [cite: 146]
        """
        #create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        #create output filename based on machine name and input string
        safe_input = input_string.replace("/", "_").replace("\\", "_")
        output_filename = f"output/{self.machine_name}_{safe_input}.txt"
        
        #open output file for writing
        with open(output_filename, 'w', encoding='utf-8') as f:
            def output_print(*args, **kwargs):
                """Print to both console and file"""
                #get separator and end from kwargs, or use defaults
                sep = kwargs.get('sep', ' ')
                end = kwargs.get('end', '\n')
                
                #create message string
                message = sep.join(str(arg) for arg in args) + end
                
                #print to console 
                print_kwargs = {k: v for k, v in kwargs.items() if k not in ['file']}
                print(*args, **print_kwargs)
                
                #write to file
                f.write(message)
                f.flush()
            
            output_print(f"Tracing NTM: {self.machine_name} on input '{input_string}'")

            # Initial Configuration: ["", start_state, input_string]
            # Note: Represent configuration as triples (left, state, right) [cite: 156]
            initial_config = ["", self.start_state, input_string]

            # The tree is a list of lists of configurations
            tree = [[initial_config]]

            #backpointers for final path reconstruction
            parent = {id(initial_config): None}

            depth = 0
            accepted = False

            while depth < max_depth and not accepted:
                current_level = tree[-1]
                next_level = []
                all_rejected = True

                # TODO: STUDENT IMPLEMENTATION NEEDED
                # 1. Iterate through every config in current_level.
                # 2. Check if config is Accept (Stop and print success) [cite: 179]
                # 3. Check if config is Reject (Stop this branch only) [cite: 181]
                # 4. If not Accept/Reject, find valid transitions in self.transitions.
                # 5. If no explicit transition exists, treat as implicit Reject.
                # 6. Generate children configurations and append to next_level[cite: 148].
                for config in current_level:
                    left, state, right = config

                    #accept check
                    if state == self.accept_state:   # [cite: 179]
                        output_print(f"String accepted in {depth} steps.")
                        self.print_trace_path(config, parent, output_print)
                        accepted = True
                        break  # stop BFS

                    #reject check
                    if state == self.reject_state:
                        continue

                    #if we reach here, there exists at least one non-reject
                    all_rejected = False

                    #determine head read symbol
                    head = right[0] if right else BLANK

                    #find all valid transitions
                    valid_transitions = self.get_transitions(state, (head,))

                    #if none, implicit reject do nothing — this branch dies
                    if not valid_transitions:
                        continue

                    #generate children
                    for t in valid_transitions:
                        next_state = t['next']
                        write_symbol = t['write'][0]
                        move = t['move'][0]

                        #initialize new config based on move direction
                        new_left = left
                        new_right = right

                        #write to tape and move head
                        if move == "R":
                            #write symbol and move right: written symbol goes to left, head moves to next position
                            new_left = left + write_symbol
                            if right:
                                new_right = right[1:] if len(right) > 1 else ""
                            else:
                                new_right = ""  #blank after moving past the end (empty string represents blank)

                        elif move == "L":
                            #write symbol at current head position first
                            if right:
                                new_right = write_symbol + right[1:]
                            else:
                                new_right = write_symbol
                            #move head left
                            if left:
                                new_right = left[-1] + new_right
                                new_left = left[:-1]
                            else:
                                #moving left from left edge creates a blank [cite: tape rules]
                                new_right = BLANK + new_right
                                new_left = ""

                        else:  #stay case
                            #just write, don't move
                            if right:
                                new_right = write_symbol + right[1:]
                            else:
                                new_right = write_symbol

                        child = [new_left, next_state, new_right]
                        parent[id(child)] = config
                        next_level.append(child)


                # Placeholder for logic:
                if not next_level and all_rejected and not accepted:
                    # TODO: Handle "String rejected" output [cite: 258]
                    output_print(f"String rejected in {depth} steps.")
                    return

                if accepted:
                    return

                tree.append(next_level)
                depth += 1

                if depth >= max_depth:
                    output_print(f"Execution stopped after {max_depth} steps.")  # [cite: 259]

    def print_trace_path(self, final_config, parent, output_print):
        """
        Backtrack using parent pointers and print the path taken.
        Ref: Section 4.2 [cite: 165]
        """
        path = []
        node = final_config

        while node is not None:
            path.append(node)
            node = parent[id(node)]

        path.reverse()

        output_print("\nTrace path:")
        depth = 0
        for left, state, right in path:
            output_print(f"Step {depth}:  {left} [{state}] {right}")
            depth += 1
