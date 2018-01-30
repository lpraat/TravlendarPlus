import unittest

from src.commandhandler.validate_data import validate_name, validate_password, validate_email


class TestValidation(unittest.TestCase):

    def test_validations(self):

        self.assertTrue(validate_email('pratissolil@gmail.com'))
        self.assertFalse(validate_email('@.it_prova@'))
        self.assertTrue(validate_name('Mario'))
        self.assertTrue(validate_name('Rossi'))
        self.assertFalse(validate_name('123kappa'))
        self.assertTrue(validate_password('prova$£$=%!!!!'))
        self.assertFalse(validate_password('short'))
