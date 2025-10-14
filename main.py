import regeng
import sys

def run_test(pattern, test_cases, expected_results, test_name=""):
    """Run tests for a specific regex pattern"""
    print(f"\n=== Testing pattern: {pattern} {test_name} ===")
    
    try:
        rgx = regeng.Regex(pattern)
    except Exception as e:
        print(f"ERROR: Failed to compile pattern '{pattern}': {str(e)}")
        return False
    
    all_passed = True
    
    for i, (test, expected) in enumerate(zip(test_cases, expected_results)):
        result = rgx.search(test)
        passed = (result is not None) == expected
        status = "PASS" if passed else "FAIL"
        
        if result:
            match_info = f"Match: '{result.group}' at {result.span}"
        else:
            match_info = "No match"
        
        print(f"  {status} - '{test}' {'should' if expected else 'should not'} match: {match_info}")
        
        if not passed:
            all_passed = False
    
    return all_passed

def run_all_tests():
    """Run all regex tests"""
    print("=== Regex Engine Test Suite ===")
    
    tests = [
        # Basic character matching
        {
            "pattern": "a",
            "test_cases": ["a", "ab", "ba", ""],
            "expected": [True, True, True, False],
            "name": "(single character)"
        },
        
        # Character classes
        {
            "pattern": "[0-9]",
            "test_cases": ["0", "9", "a", "123", ""],
            "expected": [True, True, False, True, False],
            "name": "(digit)"
        },
        {
            "pattern": "[a-z]",
            "test_cases": ["a", "z", "A", "abc", ""],
            "expected": [True, True, False, True, False],
            "name": "(lowercase letter)"
        },
        {
            "pattern": "[a-zA-Z]",
            "test_cases": ["a", "Z", "0", "aB", ""],
            "expected": [True, True, False, True, False],
            "name": "(any letter)"
        },
        {
            "pattern": "[a-zA-Z0-9_]",
            "test_cases": ["a", "Z", "0", "_", "!", ""],
            "expected": [True, True, True, True, False, False],
            "name": "(alphanumeric + underscore)"
        },
        
        # Quantifiers
        {
            "pattern": "a*",
            "test_cases": ["", "a", "aa", "aaa", "b"],
            "expected": [True, True, True, True, True],
            "name": "(zero or more a)"
        },
        {
            "pattern": "a+",
            "test_cases": ["", "a", "aa", "aaa", "b", "ba"],
            "expected": [False, True, True, True, False, True],
            "name": "(one or more a)"
        },
        {
            "pattern": "a?",
            "test_cases": ["", "a", "aa", "b"],
            "expected": [True, True, True, True],
            "name": "(zero or one a)"
        },
        
        # Combinations
        {
            "pattern": "[0-9]+",
            "test_cases": ["", "0", "123", "a123", "123a"],
            "expected": [False, True, True, True, True],
            "name": "(one or more digits)"
        },
        # Special character classes
        {
            "pattern": "\\d+",
            "test_cases": ["", "0", "123", "a123", "123a"],
            "expected": [False, True, True, True, True],
            "name": "(\\d - one or more digits)"
        },
        {
            "pattern": "\\w+",
            "test_cases": ["", "abc", "123", "abc_123", "!@#"],
            "expected": [False, True, True, True, False],
            "name": "(\\w - one or more word characters)"
        },
        {
            "pattern": "\\s+",
            "test_cases": ["", " ", "\t\n", "a b", "a"],
            "expected": [False, True, True, True, False],
            "name": "(\\s - one or more whitespace characters)"
        },
        {
            "pattern": "[a-z][0-9]",
            "test_cases": ["a1", "z9", "A1", "a", "1"],
            "expected": [True, True, False, False, False],
            "name": "(letter followed by digit)"
        },
        {
            "pattern": "(ab)+",
            "test_cases": ["", "ab", "abab", "aba", "ba"],
            "expected": [False, True, True, True, False],
            "name": "(one or more ab)"
        },
        {
            "pattern": "a|b",
            "test_cases": ["a", "b", "c", "ab"],
            "expected": [True, True, False, True],
            "name": "(a or b)"
        },
    ]
    
    results = []
    
    for test in tests:
        result = run_test(
            test["pattern"], 
            test["test_cases"], 
            test["expected"],
            test.get("name", "")
        )
        results.append(result)
    
    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r)
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}/{total} test patterns")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)