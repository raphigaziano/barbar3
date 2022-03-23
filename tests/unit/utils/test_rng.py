import unittest
from unittest.mock import patch
import random

from barbarian.utils.rng import Rng, RngError, DiceError, _RngMeta


class TestRngRoot(unittest.TestCase):

    def setUp(self):
        Rng.rngs.clear()
        Rng.root = None

    def test_root_rng_initialization(self):
        Rng.init_root()
        self.assertIsNotNone(Rng._root)

    def test_root_rng_initialization_with_given_seed(self):
        Rng.init_root('123')
        self.assertEqual(Rng._root.initial_seed, '123')

    @unittest.skip("Need to decide if that's the behaviour we want")
    def test_resetting_root_rng_is_a_noop(self):
        Rng.init_root()
        initial_root_rng = Rng._root
        Rng.init_root()
        self.assertEqual(initial_root_rng, Rng._root)

    def test_initial_seeding(self):
        # Starting with no seed
        Rng.init_root()
        Rng.add_rng('sub')

        # Convert to str to simulate copying the initial seed from the 
        # terminal and pastinh it as an arg to the client.
        initial_root_seed = str(Rng.root.initial_seed)
        initial_sub_seed = str(Rng.rngs['sub'].initial_seed)

        Rng.root = None
        # Restarting with the previous seed
        Rng.init_root(initial_root_seed)
        Rng.add_rng('sub')

        # All rngs should have the same seed as during the first run
        self.assertEqual(Rng.root.initial_seed, initial_root_seed)
        self.assertEqual(Rng.rngs['sub'].initial_seed, initial_sub_seed)


class TestAddRng(unittest.TestCase):

    def setUp(self):
        Rng.rngs.clear()
        Rng.init_root()

    def test_add_rng(self):
        Rng.add_rng('test')
        self.assertIn('test', Rng._rngs)

    def test_add_gng_with_given_seed(self):
        Rng.add_rng('test', '123')
        self.assertEqual(Rng._rngs['test'].initial_seed, '123')

    def test_access_named_rng_from_class(self):
        Rng.add_rng('test')
        self.assertTrue(hasattr(Rng, 'test'))
        self.assertIsNotNone(Rng.test)


class TestMethodDelegation(unittest.TestCase):

    def setUp(self):
        Rng.rngs.clear()
        Rng.root = None

    def test_access_to_root_random_methods(self):
        Rng.init_root()
        self.assertEqual(Rng.choice, Rng._root.choice)

    def test_delegation_to_random_module_if_no_root_rng_is_defined(self):
        self.assertEqual(Rng.choice, random.choice)

    def test_access_to_nonexisting_method_still_raises(self):
        Rng.init_root()
        self.assertRaises(AttributeError, getattr, Rng, 'i_dont_exist')


class TestRandomHelpers(unittest.TestCase):

    def setUp(self):
        Rng.init_root()

    @patch('barbarian.utils.rng._Rng.randint', return_value=3)
    def test_roll_dice(self, mocked_randint):
        res  = Rng.roll_dice(1, 6, 0)
        self.assertEqual(res, 3)
        mocked_randint.assert_called_with(1, 6)

        res  = Rng.roll_dice(1, 20, 0)
        self.assertEqual(res, 3)
        mocked_randint.assert_called_with(1, 20)

    @patch('barbarian.utils.rng._Rng.randint', return_value=3)
    def test_roll_several_dice(self, mocked_randint):
        res  = Rng.roll_dice(3, 6, 0)
        self.assertEqual(res, 9)
        self.assertEqual(mocked_randint.call_count, 3)

    @patch('barbarian.utils.rng._Rng.randint', return_value=3)
    def test_roll_dice_apply_modifier(self, mocked_randint):
        res  = Rng.roll_dice(1, 6, 1)
        self.assertEqual(res, 4)
        mocked_randint.assert_called_with(1, 6)

        res  = Rng.roll_dice(1, 6, -1)
        self.assertEqual(res, 2)
        mocked_randint.assert_called_with(1, 6)

    @patch('barbarian.utils.rng._Rng.randint', return_value=3)
    def test_roll_dice_modifier_applied_after_rolls(self, _):
        res  = Rng.roll_dice(2, 6, 1)
        self.assertEqual(res, 7)

        res  = Rng.roll_dice(2, 6, -1)
        self.assertEqual(res, 5)

    @patch('barbarian.utils.rng._Rng.randint', return_value=3)
    def test_roll_dice_result_always_exceed_zero(self, _):
        res = Rng.roll_dice(1, 4, -10)
        self.assertEqual(res, 1)

    @patch('barbarian.utils.rng._Rng.roll_dice', return_value=3)
    def test_roll_dice_str(self, mocked_rd):
        res = Rng.roll_dice_str('1d6')
        self.assertEqual(res, 3)
        mocked_rd.assert_called_with(1, 6, 0)

        res = Rng.roll_dice_str('1D6')
        self.assertEqual(res, 3)
        mocked_rd.assert_called_with(1, 6, 0)

        res = Rng.roll_dice_str('3D12')
        mocked_rd.assert_called_with(3, 12, 0)

        res = Rng.roll_dice_str('1d4+3')
        mocked_rd.assert_called_with(1, 4, 3)

        res = Rng.roll_dice_str('2d8-2')
        mocked_rd.assert_called_with(2, 8, -2)

    def test_roll_dice_str_invalid_dice_separator(self):
        self.assertRaises(DiceError, Rng.roll_dice_str, '2f8')
        self.assertRaises(DiceError, Rng.roll_dice_str, '2WAT8')
        self.assertRaises(DiceError, Rng.roll_dice_str, '28')
        self.assertRaises(DiceError, Rng.roll_dice_str, '2.8')

    def test_roll_dice_str_invalid_mod_separator(self):
        self.assertRaises(DiceError, Rng.roll_dice_str, '2d8{}8')
        self.assertRaises(DiceError, Rng.roll_dice_str, '2D8B8')

    def test_roll_dice_invalid_values(self):
        self.assertRaises(DiceError, Rng.roll_dice_str, '3do')
        self.assertRaises(DiceError, Rng.roll_dice_str, 'ad6')
        self.assertRaises(DiceError, Rng.roll_dice_str, '3d20-X')
        self.assertRaises(DiceError, Rng.roll_dice_str, 'ado')
        self.assertRaises(DiceError, Rng.roll_dice_str, ';DW$')
        self.assertRaises(DiceError, Rng.roll_dice_str, '8dWUT+lol')

    def test_roll_table(self):

        table = [
            (10, 'one'),
            (1, 'two'),
            (3, 'three'),
        ]
        total_weights = 14

        for rval in range(1, total_weights + 1):
            with patch(
                'barbarian.utils.rng._Rng.randint', return_value=rval
            ):
                chosen = Rng.roll_table(table)
                if rval in range(1, 11):
                    self.assertEqual('one', chosen)
                elif rval == 11:
                    self.assertEqual('two', chosen)
                elif 11 < rval < total_weights + 1:
                    self.assertEqual('three', chosen)
                else:
                    self.fail(f'Something is wrong with roll {rval}')

    def test_roll_table_all_weight_equal(self):

        table = [
            (1, 'one'),
            (1, 'two'),
            (1, 'three'),
        ]

        with patch(
            'barbarian.utils.rng._Rng.randint', return_value=1
        ):
            self.assertEqual('one', Rng.roll_table(table))
        with patch(
            'barbarian.utils.rng._Rng.randint', return_value=2
        ):
            self.assertEqual('two', Rng.roll_table(table))
        with patch(
            'barbarian.utils.rng._Rng.randint', return_value=3
        ):
            self.assertEqual('three', Rng.roll_table(table))

    def test_roll_table_negative_weights(self):
        table = [(-10, 'woop'), (-1, 'wee'), (2, 'woo')]
        self.assertRaises(RngError, Rng.roll_table, table)

    def test_roll_table_empty_table(self):
        self.assertRaises(RngError, Rng.roll_table, [])
