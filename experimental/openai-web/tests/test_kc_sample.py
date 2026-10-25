"""Compiler boundary: account for source rows, independent of expected order."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
from build_kc_sample import candidate_region


class SampleRosterTests(unittest.TestCase):
    reading = '''U.S. REPRESENTATIVE
DISTRICT 5
Vote for One
RICK BRATTIN REP
EMANUEL CLEAVER, II DEM
RANDALL (RANDY) LIB
LANGKRAEHR
Write-in
STATE AUDITOR
OF MISSOURI
Vote for One
OTHER PERSON REP
Write-in
'''
    people = 'RANDALL (RANDY) LANGKRAEHR|LIB;EMANUEL CLEAVER, II|DEM;RICK BRATTIN|REP'

    def test_source_order_and_wrapped_party_are_preserved_inside_contest_region(self):
        rows, instruction = candidate_region(self.reading, 'us-house-5', self.people)
        self.assertEqual([r['printed_name'] for r in rows],
                         ['RICK BRATTIN', 'EMANUEL CLEAVER, II', 'RANDALL (RANDY) LANGKRAEHR'])
        self.assertEqual([r['ballot_order'] for r in rows], [1, 2, 3])
        self.assertEqual(self.reading[instruction['start']:instruction['end']], 'Vote for One')

    def test_extra_status_unknown_candidate_and_name_from_another_contest_fail_closed(self):
        for extra in ['ANOTHER PERSON GRN\n', 'NO CANDIDATE FILED REP\n', 'RICK BRATTIN REP\n']:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                candidate_region(self.reading.replace('Write-in', extra + 'Write-in', 1), 'us-house-5', self.people)
        with self.assertRaises(ValueError):
            candidate_region(self.reading.replace('RICK BRATTIN REP\n', '', 1), 'us-house-5', self.people)
