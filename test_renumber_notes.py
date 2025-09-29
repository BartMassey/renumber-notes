#!/usr/bin/env python3
"""Test suite for renumber-notes.py"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestRenumberNotes(unittest.TestCase):
    """Test cases for renumber-notes.py"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = tempfile.mkdtemp(prefix="renumber_test_")
        self.script = Path(__file__).parent / "renumber-notes.py"
        self.orig_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        os.chdir(self.orig_dir)
        shutil.rmtree(self.test_dir)

    def run_script(self, *args):
        """Run renumber-notes.py with given arguments"""
        cmd = [str(self.script)] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def create_files(self, filenames):
        """Create test files"""
        for name in filenames:
            Path(name).touch()

    def get_files(self):
        """Get sorted list of files in test directory"""
        return sorted([f.name for f in Path(self.test_dir).iterdir() if f.is_file()])

    def test_basic_increment_two_digits(self):
        """Test basic increment with 2-digit prefixes"""
        self.create_files(["01-intro.md", "02-basics.md", "03-advanced.md"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["02-intro.md", "03-basics.md", "04-advanced.md"])

    def test_basic_increment_one_digit(self):
        """Test basic increment with 1-digit prefixes"""
        self.create_files(["1-intro.md", "2-basics.md", "3-advanced.md"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["2-intro.md", "3-basics.md", "4-advanced.md"])

    def test_basic_increment_three_digits(self):
        """Test basic increment with 3-digit prefixes"""
        self.create_files(["001-intro.md", "002-basics.md", "003-advanced.md"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["002-intro.md", "003-basics.md", "004-advanced.md"])

    def test_decrement(self):
        """Test decrementing file numbers"""
        self.create_files(["05-intro.md", "06-basics.md", "07-advanced.md"])
        result = self.run_script("--no-git-mv", "-2")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["03-intro.md", "04-basics.md", "05-advanced.md"])

    def test_large_increment(self):
        """Test large increment"""
        self.create_files(["01-intro.md", "02-basics.md"])
        result = self.run_script("--no-git-mv", "+10")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["11-intro.md", "12-basics.md"])

    def test_start_parameter(self):
        """Test starting from specific file number"""
        self.create_files(["01-intro.md", "02-basics.md", "03-advanced.md"])
        result = self.run_script("--no-git-mv", "+1", "2")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["01-intro.md", "03-basics.md", "04-advanced.md"])

    def test_manual_digits_override(self):
        """Test --digits flag to override digit count"""
        self.create_files(["1-intro.md", "2-basics.md"])
        result = self.run_script("--no-git-mv", "--digits", "3", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["002-intro.md", "003-basics.md"])

    def test_preview_mode(self):
        """Test preview mode doesn't modify files"""
        self.create_files(["01-intro.md", "02-basics.md"])
        result = self.run_script("--no-git-mv", "--preview", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["01-intro.md", "02-basics.md"])
        self.assertIn("mv 01-intro.md 02-intro.md", result.stdout)
        self.assertIn("mv 02-basics.md 03-basics.md", result.stdout)

    def test_gap_in_numbers(self):
        """Test files with gaps in numbering"""
        self.create_files(["01-intro.md", "02-basics.md", "05-advanced.md"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["02-intro.md", "03-basics.md", "05-advanced.md"])

    def test_mixed_extensions(self):
        """Test files with different extensions"""
        self.create_files(["01-intro.md", "02-basics.txt", "03-advanced.pdf"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["02-intro.md", "03-basics.txt", "04-advanced.pdf"])

    def test_no_numbered_files(self):
        """Test with no numbered files"""
        self.create_files(["readme.md", "notes.txt"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["notes.txt", "readme.md"])

    def test_non_numbered_files_ignored(self):
        """Test that non-numbered files are not affected"""
        self.create_files(["01-intro.md", "readme.md", "02-basics.md"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["02-intro.md", "03-basics.md", "readme.md"])

    def test_auto_expand_digits(self):
        """Test automatic digit expansion when needed"""
        self.create_files(["8-intro.md", "9-basics.md"])
        result = self.run_script("--no-git-mv", "+5")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["13-intro.md", "14-basics.md"])

    def test_git_mv_with_git_repo(self):
        """Test git mv is used when in git repository"""
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)
        self.create_files(["01-intro.md", "02-basics.md"])
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], capture_output=True)

        result = self.run_script("--preview", "+1")
        self.assertEqual(result.returncode, 0)
        self.assertIn("git mv", result.stdout)

    def test_no_git_mv_flag(self):
        """Test --no-git-mv flag forces regular mv"""
        subprocess.run(["git", "init"], capture_output=True)
        self.create_files(["01-intro.md", "02-basics.md"])

        result = self.run_script("--no-git-mv", "--preview", "+1")
        self.assertEqual(result.returncode, 0)
        self.assertIn("mv 01-intro.md", result.stdout)
        self.assertNotIn("git mv", result.stdout)

    def test_invariant_prefix(self):
        """Test files with invariant numeric prefix"""
        self.create_files(["02-1-intro.md", "02-2-basics.md", "02-3-advanced.md"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["02-2-intro.md", "02-3-basics.md", "02-4-advanced.md"])

    def test_invariant_prefix_decrement(self):
        """Test decrement with invariant numeric prefix"""
        self.create_files(["week2-05-intro.md", "week2-06-basics.md", "week2-07-advanced.md"])
        result = self.run_script("--no-git-mv", "-2")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["week2-03-intro.md", "week2-04-basics.md", "week2-05-advanced.md"])

    def test_invariant_prefix_with_gaps(self):
        """Test prefix detection with gaps in numbering"""
        self.create_files(["lec-01-intro.md", "lec-02-basics.md", "lec-05-advanced.md"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["lec-02-intro.md", "lec-03-basics.md", "lec-05-advanced.md"])

    def test_preserve_leading_zeros(self):
        """Test that leading zeros are preserved"""
        self.create_files(["001-intro.md", "002-basics.md", "003-advanced.md"])
        result = self.run_script("--no-git-mv", "+7")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["008-intro.md", "009-basics.md", "010-advanced.md"])

    def test_expand_digits_when_needed(self):
        """Test that digit width expands when result exceeds current width"""
        self.create_files(["08-intro.md", "09-basics.md"])
        result = self.run_script("--no-git-mv", "+1")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        # Should expand to 2 digits for 10
        self.assertEqual(files, ["09-intro.md", "10-basics.md"])

    def test_preserve_leading_zeros_with_prefix(self):
        """Test leading zeros preserved with invariant prefix"""
        self.create_files(["week2-001-intro.md", "week2-002-basics.md", "week2-003-advanced.md"])
        result = self.run_script("--no-git-mv", "+10")
        self.assertEqual(result.returncode, 0)
        files = self.get_files()
        self.assertEqual(files, ["week2-011-intro.md", "week2-012-basics.md", "week2-013-advanced.md"])


if __name__ == "__main__":
    unittest.main()