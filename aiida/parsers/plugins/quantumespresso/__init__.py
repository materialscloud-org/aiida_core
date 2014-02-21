from aiida.parsers.exceptions import OutputParsingError

class QEOutputParsingError(OutputParsingError):
    pass
    # def __init__(self,message):
    #     wrappedmessage = "Error parsing Quantum Espresso PW output: " + message
    #     super(QEOutputParsingError,self).__init__(wrappedmessage)
    #     self.message = wrappedmessage
    #     self.module = "qe-pw"

def convert_qe2aiida_structure(output_dict,input_structure=None):
    """
    Receives the dictionary cell parsed from quantum espresso
    Convert it into an AiiDA structure object
    """
    from aiida.orm import DataFactory
    StructureData = DataFactory('structure')

    cell_dict = output_dict['cell']

    # If I don't have any help, I will set up the cell as it is in QE
    if not input_structure:
        
        s = StructureData(cell=cell_dict['lattice_parameters'])
        for atom in cell_dict['atoms']:
            s.append_atom( position=tuple(atom[1]),symbols=[ atom[0] ] )
            
    else:
        
        s = input_structure.copy()
        s.reset_cell(cell_dict['lattice_vectors'])
        new_pos = [ i[1] for i in cell_dict['atoms'] ]
        s.reset_sites_positions( new_pos )
    
    return s