import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');
export let responseTime = new Trend('response_time');

// Test configuration
export let options = {
  // Scenario: Gradual ramp-up to 20 RPS
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 20 }, // Stay at 20 users (≈20 RPS)
    { duration: '2m', target: 0 },  // Ramp down
  ],
  
  // Thresholds - Performance targets
  thresholds: {
    http_req_duration: ['p(95)<200'], // P95 latency < 200ms
    http_req_failed: ['rate<0.05'],   // Error rate < 5%
    errors: ['rate<0.05'],            // Custom error rate < 5%
  },
};

// Test data
const BASE_URL = __ENV.BASE_URL || 'https://your-domain.com';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'your-test-jwt-token';

const AGENT_TYPES = ['praisonai', 'crewai', 'ag2'];

const TEST_TASKS = [
  'Analyze the current market trends in technology',
  'Summarize the latest developments in artificial intelligence',
  'Create a business plan for a startup in the healthcare sector',
  'Write a technical overview of cloud computing benefits',
  'Generate insights about sustainable energy solutions',
  'Explain the impact of blockchain technology on finance',
  'Provide recommendations for improving team productivity',
  'Analyze customer satisfaction data and suggest improvements',
];

// Helper functions
function getRandomAgentType() {
  return AGENT_TYPES[Math.floor(Math.random() * AGENT_TYPES.length)];
}

function getRandomTask() {
  return TEST_TASKS[Math.floor(Math.random() * TEST_TASKS.length)];
}

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${AUTH_TOKEN}`,
  };
}

// Main test function
export default function() {
  // Test 1: Health check (lightweight)
  let healthResponse = http.get(`${BASE_URL}/v1/health`);
  
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 100ms': (r) => r.timings.duration < 100,
  });
  
  // Test 2: Get agent info
  let agentInfoResponse = http.get(`${BASE_URL}/v1/agents`, {
    headers: getHeaders(),
  });
  
  check(agentInfoResponse, {
    'agent info status is 200': (r) => r.status === 200,
    'agent info has available agents': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.available_agents && body.available_agents.length > 0;
      } catch (e) {
        return false;
      }
    },
  });
  
  // Test 3: Agent execution (main functionality)
  const agentType = getRandomAgentType();
  const task = getRandomTask();
  
  const payload = JSON.stringify({
    task: task,
    agent_type: agentType,
    context: {
      test: true,
      load_test: true,
      timestamp: new Date().toISOString(),
    }
  });
  
  const startTime = new Date().getTime();
  
  let agentResponse = http.post(`${BASE_URL}/v1/answer`, payload, {
    headers: getHeaders(),
    timeout: '60s', // Allow up to 60s for agent execution
  });
  
  const endTime = new Date().getTime();
  const responseTime_ms = endTime - startTime;
  
  // Record custom metrics
  responseTime.add(responseTime_ms);
  
  // Check response
  const agentCheckPassed = check(agentResponse, {
    'agent execution status is 200': (r) => r.status === 200,
    'agent response has success field': (r) => {
      try {
        const body = JSON.parse(r.body);
        return 'success' in body;
      } catch (e) {
        return false;
      }
    },
    'agent execution time < 30s': (r) => r.timings.duration < 30000,
  });
  
  // Record error if checks failed
  errorRate.add(!agentCheckPassed);
  
  // Log response for debugging (only for failed requests)
  if (!agentCheckPassed) {
    console.log(`Failed request: ${agentResponse.status} - ${agentResponse.body}`);
    console.log(`Agent type: ${agentType}, Task length: ${task.length}`);
  }
  
  // Test 4: Session creation (less frequent)
  if (Math.random() < 0.1) { // 10% of requests
    let sessionResponse = http.post(`${BASE_URL}/v1/sessions`, 
      JSON.stringify({ session_name: `Load Test Session ${Date.now()}` }), 
      { headers: getHeaders() }
    );
    
    check(sessionResponse, {
      'session creation status is 200': (r) => r.status === 200,
      'session response has session_id': (r) => {
        try {
          const body = JSON.parse(r.body);
          return 'session_id' in body;
        } catch (e) {
          return false;
        }
      },
    });
  }
  
  // Think time - simulate real user behavior
  sleep(Math.random() * 2 + 1); // 1-3 seconds
}

// Setup function - runs once before the test
export function setup() {
  console.log('Starting load test...');
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Auth Token: ${AUTH_TOKEN ? 'Present' : 'Missing'}`);
  console.log(`Available agents: ${AGENT_TYPES.join(', ')}`);
  
  // Verify the service is accessible
  let healthCheck = http.get(`${BASE_URL}/v1/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`Service not accessible: ${healthCheck.status}`);
  }
  
  console.log('Service health check passed');
  return { startTime: new Date() };
}

// Teardown function - runs once after the test
export function teardown(data) {
  const endTime = new Date();
  const duration = (endTime - data.startTime) / 1000;
  console.log(`Load test completed in ${duration} seconds`);
}

// Handle summary - custom summary output
export function handleSummary(data) {
  console.log('=== LOAD TEST SUMMARY ===');
  console.log(`Total requests: ${data.metrics.http_reqs.values.count}`);
  console.log(`Request rate: ${data.metrics.http_reqs.values.rate}/s`);
  console.log(`Average response time: ${data.metrics.http_req_duration.values.avg}ms`);
  console.log(`P95 response time: ${data.metrics.http_req_duration.values['p(95)']}ms`);
  console.log(`Error rate: ${data.metrics.http_req_failed.values.rate * 100}%`);
  
  // Performance analysis
  const p95_target = 200; // ms
  const error_rate_target = 0.05; // 5%
  
  const p95_actual = data.metrics.http_req_duration.values['p(95)'];
  const error_rate_actual = data.metrics.http_req_failed.values.rate;
  
  console.log('\n=== PERFORMANCE ANALYSIS ===');
  console.log(`P95 Latency: ${p95_actual}ms (target: <${p95_target}ms) ${p95_actual < p95_target ? '✅' : '❌'}`);
  console.log(`Error Rate: ${(error_rate_actual * 100).toFixed(2)}% (target: <${error_rate_target * 100}%) ${error_rate_actual < error_rate_target ? '✅' : '❌'}`);
  
  // Generate detailed report
  return {
    'load-test-summary.json': JSON.stringify(data, null, 2),
    stdout: '', // Suppress default k6 output
  };
} 