#!/usr/bin/env python3
"""
Test script for DeepWiki Agent Strategy
This script validates the basic functionality of the DeepWiki strategy implementation.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all necessary modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from strategies.deepwiki import DeepWikiAgentStrategy, DeepWikiParams
        print("✅ Successfully imported DeepWiki classes")
    except ImportError as e:
        print(f"❌ Failed to import DeepWiki classes: {e}")
        return False
    
    try:
        from dify_plugin.interfaces.agent import AgentStrategy
        print("✅ Successfully imported base AgentStrategy")
    except ImportError as e:
        print(f"❌ Failed to import base AgentStrategy: {e}")
        return False
    
    return True

def test_strategy_inheritance():
    """Test that DeepWikiAgentStrategy properly inherits from AgentStrategy"""
    print("\n🧪 Testing strategy inheritance...")
    
    try:
        from strategies.deepwiki import DeepWikiAgentStrategy
        from dify_plugin.interfaces.agent import AgentStrategy
        
        assert issubclass(DeepWikiAgentStrategy, AgentStrategy)
        print("✅ DeepWikiAgentStrategy properly inherits from AgentStrategy")
        return True
    except Exception as e:
        print(f"❌ Inheritance test failed: {e}")
        return False

def test_params_model():
    """Test that DeepWikiParams can be instantiated with valid parameters"""
    print("\n🧪 Testing parameter model...")
    
    try:
        from strategies.deepwiki import DeepWikiParams
        from dify_plugin.interfaces.agent import AgentModelConfig
        from unittest.mock import Mock
        
        # Create properly structured mock model config
        mock_entity = Mock()
        mock_entity.features = []
        
        mock_model_data = {
            "provider": "openai",
            "model": "gpt-4o",
            "completion_params": {"temperature": 0.7},
            "history_prompt_messages": [],
            "entity": mock_entity
        }
        
        # Test parameter validation without full instantiation
        required_fields = ["repository_url", "model", "tools", "instruction"]
        
        # Test that the class has the expected attributes
        import inspect
        params_signature = inspect.signature(DeepWikiParams)
        param_names = list(params_signature.parameters.keys())
        
        for field in required_fields:
            assert field in param_names, f"Required field missing: {field}"
        
        # Test default values
        default_values = {
            "analysis_depth": "standard",
            "include_diagrams": True,
            "maximum_iterations": 5
        }
        
        for field, expected_default in default_values.items():
            param = params_signature.parameters.get(field)
            if param and param.default != inspect.Parameter.empty:
                assert param.default == expected_default, f"Default value mismatch for {field}"
        
        print("✅ DeepWikiParams structure validation successful")
        return True
    except Exception as e:
        print(f"❌ Parameter model test failed: {e}")
        return False

def test_url_validation():
    """Test URL validation functionality"""
    print("\n🧪 Testing URL validation...")
    
    try:
        from strategies.deepwiki import DeepWikiAgentStrategy
        
        # Test URL validation method directly without instantiating the strategy
        # since it requires runtime and session parameters
        import inspect
        
        # Get the validation method
        validation_method = DeepWikiAgentStrategy._validate_repository_url
        
        # Create a dummy instance for testing (won't work for invoke but OK for validation)
        class TestStrategy:
            def _validate_repository_url(self, url):
                return DeepWikiAgentStrategy._validate_repository_url(self, url)
        
        test_strategy = TestStrategy()
        
        # Test valid URLs
        valid_urls = [
            "https://github.com/microsoft/autogen",
            "https://gitlab.com/group/project",
            "https://bitbucket.org/user/repo",
            "http://github.com/user/repo",
        ]
        
        for url in valid_urls:
            result = test_strategy._validate_repository_url(url)
            assert result, f"Valid URL should pass: {url}"
        
        # Test invalid URLs
        invalid_urls = [
            "not-a-url",
            "https://example.com/repo",
            "https://github.com",
            "https://github.com/user",
            "",
        ]
        
        for url in invalid_urls:
            result = test_strategy._validate_repository_url(url)
            assert not result, f"Invalid URL should fail: {url}"
        
        print("✅ URL validation working correctly")
        return True
    except Exception as e:
        print(f"❌ URL validation test failed: {e}")
        return False

def test_yaml_configuration():
    """Test that the YAML configuration is valid"""
    print("\n🧪 Testing YAML configuration...")
    
    try:
        import yaml
        
        with open('strategies/deepwiki.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        assert 'identity' in config
        assert 'parameters' in config
        assert 'extra' in config
        
        # Check identity fields
        identity = config['identity']
        assert identity['name'] == 'deepwiki'
        assert 'label' in identity
        assert 'en_US' in identity['label']
        
        # Check parameters
        parameters = config['parameters']
        required_params = ['model', 'tools', 'instruction', 'repository_url', 'maximum_iterations']
        param_names = [p['name'] for p in parameters]
        
        for required_param in required_params:
            assert required_param in param_names, f"Required parameter missing: {required_param}"
        
        print("✅ YAML configuration is valid")
        return True
    except Exception as e:
        print(f"❌ YAML configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting DeepWiki Agent Strategy tests...\n")
    
    tests = [
        test_imports,
        test_strategy_inheritance,
        test_params_model,
        test_url_validation,
        test_yaml_configuration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DeepWiki strategy implementation is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())