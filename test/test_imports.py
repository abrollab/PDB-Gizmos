import unittest

class TestImports(unittest.TestCase):

    def test_impots(self):
        try:
            import pdb_gizmpos.debugg
            import pdb_gizmpos.debugg.errors
            import pdb_gizmpos.debugg.logger
            import pdb_gizmpos.debugg.stdout
            import pdb_gizmpos.editor
            # import pdb_gizmpos.editor.PdbEditor
            import pdb_gizmpos.io.custom_args
            import pdb_gizmpos.io.infile_handler
            import pdb_gizmpos.io.loader
            import pdb_gizmpos.io.trajectory_reader
            import pdb_gizmpos.requester
            import pdb_gizmpos.requester.opm
            import pdb_gizmpos.requester.pdbtm
            import pdb_gizmpos.requester.rcsb
            import pdb_gizmpos.requester.requester
            import pdb_gizmpos.utils
            import pdb_gizmpos.utils.cpptraj_inputs
            import pdb_gizmpos.utils.finder
            import pdb_gizmpos.utils.rmsd
            import pdb_gizmpos.utils.trajmath
        except ImportError:
            self.AssertEqual(True, False)
        self.assertEqual(True, True)