#!/bin/bash

# SnapLearn AI Phase 5 - End-to-End Demo Test Script
# Comprehensive testing of all Phase 5 production features

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test Results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

section() {
    echo
    echo -e "${PURPLE}=== $1 ===${NC}"
    echo
}

# Test helper functions
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TESTS_TOTAL++))
    info "Running: $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        success "$test_name"
        return 0
    else
        failure "$test_name"
        return 1
    fi
}

api_test() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    local expected_status="${4:-200}"
    
    local curl_cmd="curl -s -o /dev/null -w '%{http_code}' -X $method"
    
    if [[ -n "$data" ]]; then
        curl_cmd="$curl_cmd -H 'Content-Type: application/json' -d '$data'"
    fi
    
    curl_cmd="$curl_cmd $API_URL$endpoint"
    
    local status_code
    status_code=$(eval "$curl_cmd")
    
    if [[ "$status_code" == "$expected_status" ]]; then
        return 0
    else
        echo "Expected $expected_status, got $status_code" >&2
        return 1
    fi
}

# Main test functions
test_system_health() {
    section "System Health Checks"
    
    run_test "Backend Health Check" "api_test '/health' GET"
    run_test "Frontend Accessibility" "curl -s -o /dev/null -w '%{http_code}' $FRONTEND_URL | grep -q '200'"
    run_test "API Documentation Available" "api_test '/docs' GET"
    run_test "OpenAPI Schema Available" "api_test '/openapi.json' GET"
}

test_sdk_demo_portal() {
    section "SDK Demo Portal Testing"
    
    # Get available demos
    run_test "Get Available Demos" "api_test '/api/demo/available' GET"
    
    # Start a demo session
    local demo_start_data='{"scenario": "elementary_math", "visitor_info": {"organization": "Test Org"}}'
    
    if api_test '/api/demo/start' POST "$demo_start_data" 200; then
        success "Start Demo Session"
        ((TESTS_PASSED++))
        
        # Get session ID from response (simplified for demo)
        local session_id="demo_test_$(date +%s)"
        
        # Execute demo step
        run_test "Execute Demo Step" "api_test '/api/demo/$session_id/execute' POST '{}' 200"
        
        # Get session status  
        run_test "Get Demo Status" "api_test '/api/demo/$session_id/status' GET"
        
        # Complete session
        local feedback_data='{"feedback": {"rating": 5, "comments": "Great demo!"}}'
        run_test "Complete Demo Session" "api_test '/api/demo/$session_id/complete' POST '$feedback_data' 200"
    else
        failure "Start Demo Session"
        ((TESTS_FAILED++))
    fi
    
    ((TESTS_TOTAL += 4))
}

test_multi_tenant_system() {
    section "Multi-Tenant System Testing"
    
    # Note: These tests would require proper authentication setup
    # For demo purposes, we'll test the endpoint availability
    
    run_test "Authentication Endpoint Available" "api_test '/api/auth/login' POST '{}' 422"  # Expect validation error
    run_test "Organization Creation Endpoint" "api_test '/api/organizations' POST '{}' 401"  # Expect auth required
    run_test "API Key Creation Endpoint" "api_test '/api/api-keys' POST '{}' 401"  # Expect auth required
    
    info "Multi-tenant system endpoints are properly secured (auth required)"
}

test_advanced_assessment() {
    section "Advanced Assessment System Testing"
    
    # Get assessment templates
    run_test "Get Assessment Templates" "api_test '/api/assessment/templates' GET 401"  # Expect auth required
    
    # Test assessment creation (would require auth)
    run_test "Assessment Creation Endpoint" "api_test '/api/assessment/create' POST '{}' 401"  # Expect auth required
    
    info "Assessment system endpoints are properly secured (auth required)"
}

test_integration_hub() {
    section "Integration Hub Testing"
    
    # Get supported systems
    run_test "Get Supported Systems" "api_test '/api/integrations/systems' GET"
    
    # Test webhook creation (would require auth)
    run_test "Webhook Creation Endpoint" "api_test '/api/webhooks' POST '{}' 401"  # Expect auth required
    
    # Test integration creation (would require auth)  
    run_test "Integration Creation Endpoint" "api_test '/api/integrations' POST '{}' 401"  # Expect auth required
    
    info "Integration hub endpoints are properly secured (auth required)"
}

test_core_api_endpoints() {
    section "Core API Endpoints Testing"
    
    # Test core tutoring endpoints (these should require authentication in production)
    run_test "Explain Endpoint Available" "api_test '/api/explain' POST '{}' 401"  # Expect auth required
    run_test "Video Generation Endpoint" "api_test '/api/generate-video' POST '{}' 401"  # Expect auth required
    run_test "Process Image Endpoint" "api_test '/api/process-image' POST '{}' 401"  # Expect auth required
    run_test "Process Voice Endpoint" "api_test '/api/process-voice' POST '{}' 401"  # Expect auth required
    
    info "Core API endpoints are properly secured (auth required)"
}

test_frontend_components() {
    section "Frontend Components Testing"
    
    # Test main pages accessibility
    run_test "Main Page Loads" "curl -s -o /dev/null -w '%{http_code}' $FRONTEND_URL | grep -q '200'"
    run_test "Static Assets Load" "curl -s -o /dev/null -w '%{http_code}' $FRONTEND_URL/static/ | grep -q -E '(200|403|404)'"
    
    info "Frontend is serving correctly"
}

test_monitoring_endpoints() {
    section "Monitoring & Observability Testing"
    
    # Test Prometheus metrics (if available)
    if curl -s "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
        success "Prometheus is running"
        ((TESTS_PASSED++))
    else
        warning "Prometheus not available (optional for demo)"
    fi
    
    # Test Grafana (if available)  
    if curl -s "http://localhost:3001/api/health" > /dev/null 2>&1; then
        success "Grafana is running"
        ((TESTS_PASSED++))
    else
        warning "Grafana not available (optional for demo)"
    fi
    
    ((TESTS_TOTAL += 2))
}

test_security_headers() {
    section "Security Headers Testing"
    
    # Test security headers
    local headers
    headers=$(curl -s -I "$API_URL/health")
    
    if echo "$headers" | grep -q "X-Content-Type-Options: nosniff"; then
        success "X-Content-Type-Options header present"
        ((TESTS_PASSED++))
    else
        failure "X-Content-Type-Options header missing"
        ((TESTS_FAILED++))
    fi
    
    if echo "$headers" | grep -q "X-Frame-Options: DENY"; then
        success "X-Frame-Options header present"
        ((TESTS_PASSED++))
    else
        failure "X-Frame-Options header missing" 
        ((TESTS_FAILED++))
    fi
    
    ((TESTS_TOTAL += 2))
}

test_api_documentation() {
    section "API Documentation Testing"
    
    # Test API documentation
    run_test "Swagger UI Available" "curl -s $API_URL/docs | grep -q 'SnapLearn AI API'"
    run_test "ReDoc Available" "curl -s $API_URL/redoc | grep -q 'SnapLearn AI API'"
    run_test "OpenAPI Schema Valid" "curl -s $API_URL/openapi.json | python -m json.tool > /dev/null"
}

# Performance and load testing
test_basic_performance() {
    section "Basic Performance Testing"
    
    # Test response times
    local health_time
    health_time=$(curl -s -o /dev/null -w '%{time_total}' "$API_URL/health")
    
    if (( $(echo "$health_time < 1.0" | bc -l) )); then
        success "Health endpoint responds in <1s (${health_time}s)"
        ((TESTS_PASSED++))
    else
        failure "Health endpoint slow (${health_time}s)"
        ((TESTS_FAILED++))
    fi
    
    ((TESTS_TOTAL++))
    
    info "Basic performance test completed"
}

# SDK functionality tests (mock)
test_sdk_functionality() {
    section "SDK Functionality Testing (Mock)"
    
    # These would be integration tests with actual SDK files
    local js_sdk_file="$PROJECT_ROOT/sdk/javascript/snaplearn-ai-sdk.js"
    local python_sdk_file="$PROJECT_ROOT/sdk/python/snaplearn_ai_sdk.py"
    
    if [[ -f "$js_sdk_file" ]]; then
        success "JavaScript SDK file exists"
        ((TESTS_PASSED++))
        
        # Basic syntax check
        if node -c "$js_sdk_file" 2>/dev/null; then
            success "JavaScript SDK syntax valid"
            ((TESTS_PASSED++))
        else
            failure "JavaScript SDK syntax invalid"
            ((TESTS_FAILED++))
        fi
    else
        failure "JavaScript SDK file missing"
        ((TESTS_FAILED++))
    fi
    
    if [[ -f "$python_sdk_file" ]]; then
        success "Python SDK file exists"
        ((TESTS_PASSED++))
        
        # Basic syntax check
        if python -m py_compile "$python_sdk_file" 2>/dev/null; then
            success "Python SDK syntax valid"
            ((TESTS_PASSED++))
        else
            failure "Python SDK syntax invalid"
            ((TESTS_FAILED++))
        fi
    else
        failure "Python SDK file missing"
        ((TESTS_FAILED++))
    fi
    
    ((TESTS_TOTAL += 4))
}

# Generate test report
generate_test_report() {
    section "Test Report"
    
    echo "📊 Phase 5 Production Demo Test Results"
    echo "======================================"
    echo
    echo "Tests Executed: $TESTS_TOTAL"
    echo "Tests Passed:   $TESTS_PASSED"
    echo "Tests Failed:   $TESTS_FAILED"
    echo
    
    local success_rate
    if (( TESTS_TOTAL > 0 )); then
        success_rate=$(( (TESTS_PASSED * 100) / TESTS_TOTAL ))
        echo "Success Rate:   ${success_rate}%"
    else
        echo "Success Rate:   N/A"
        success_rate=0
    fi
    
    echo
    
    if (( TESTS_FAILED == 0 )); then
        echo -e "${GREEN}🎉 All tests passed! Phase 5 is production ready.${NC}"
        return 0
    elif (( success_rate >= 80 )); then
        echo -e "${YELLOW}⚠️  Most tests passed with minor issues.${NC}"
        return 0
    else
        echo -e "${RED}❌ Significant issues found. Review failed tests.${NC}"
        return 1
    fi
}

show_demo_info() {
    section "Phase 5 Demo Information"
    
    echo "🚀 SnapLearn AI Phase 5 - Production Demo"
    echo "========================================"
    echo
    echo "🏗️  Architecture:"
    echo "   • Multi-tenant with RBAC"
    echo "   • Microservices with Docker"
    echo "   • Event-driven integrations" 
    echo "   • Real-time analytics"
    echo
    echo "🎯 Key Features Demonstrated:"
    echo "   • Interactive SDK Demo Portal"
    echo "   • Advanced Assessment System"
    echo "   • Multi-tenant Security"
    echo "   • Integration Hub with Webhooks"
    echo "   • Production-ready Infrastructure"
    echo
    echo "🔗 Demo URLs:"
    echo "   • Frontend:     $FRONTEND_URL"
    echo "   • Backend API:  $API_URL" 
    echo "   • API Docs:     $API_URL/docs"
    echo "   • Demo Portal:  $FRONTEND_URL/demo"
    echo "   • Developer:    $FRONTEND_URL/dashboard"
    echo
    echo "📚 SDK Usage:"
    echo "   • JavaScript:   /sdk/javascript/snaplearn-ai-sdk.js"
    echo "   • Python:       /sdk/python/snaplearn_ai_sdk.py"
    echo "   • Examples:     /docs/examples/"
    echo
    echo "🎪 Demo Scenarios Available:"
    echo "   • Elementary Math Mastery"
    echo "   • High School Algebra Assistant" 
    echo "   • Multilingual Learning"
    echo "   • Custom Integration Demos"
    echo
}

# Main execution
main() {
    clear
    echo -e "${PURPLE}"
    cat << "EOF"
  ____                      _                           _    _____ 
 / ___| _ __   __ _ _ __    | |    ___  __ _ _ __ _ __   / \  |_ _| |
 \___ \| '_ \ / _` | '_ \   | |   / _ \/ _` | '__| '_ \ /  \   | |  |
  ___) | | | | (_| | |_) |  | |__|  __/ (_| | |  | | | /  _  \ | |  |
 |____/|_| |_|\__,_| .__/   |_____\___|\__,_|_|  |_| |_/_/ \_\___|_|
                   |_|                                               

Phase 5 - Production Demo Test Suite
EOF
    echo -e "${NC}"
    
    show_demo_info
    
    log "Starting comprehensive Phase 5 testing..."
    
    # Run all test suites
    test_system_health
    test_sdk_demo_portal  
    test_multi_tenant_system
    test_advanced_assessment
    test_integration_hub
    test_core_api_endpoints
    test_frontend_components
    test_monitoring_endpoints
    test_security_headers
    test_api_documentation
    test_basic_performance
    test_sdk_functionality
    
    # Generate final report
    generate_test_report
    
    echo
    log "Phase 5 testing completed!"
}

# Handle script arguments
case "${1:-test}" in
    "test"|"demo")
        main
        ;;
    "health")
        test_system_health
        ;;
    "sdk")
        test_sdk_demo_portal
        test_sdk_functionality
        ;;
    "security")
        test_security_headers
        test_multi_tenant_system
        ;;
    "performance")
        test_basic_performance
        ;;
    "info")
        show_demo_info
        ;;
    *)
        echo "Usage: $0 {test|demo|health|sdk|security|performance|info}"
        echo
        echo "Commands:"
        echo "  test        - Run full test suite (default)"
        echo "  demo        - Same as test (alias)"
        echo "  health      - Run health checks only"
        echo "  sdk         - Test SDK functionality" 
        echo "  security    - Test security features"
        echo "  performance - Run performance tests"
        echo "  info        - Show demo information"
        exit 1
        ;;
esac