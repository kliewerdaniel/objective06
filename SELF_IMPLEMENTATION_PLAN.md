# SELF Project Implementation Plan

## Overview

This document provides detailed implementation instructions for improving the SELF project. It includes:

1. **Critical Fixes** (Priority 1) - Immediate security and data integrity issues
2. **Documentation Improvements** (Priority 2) - Enhance existing documentation
3. **UI/UX Design** (Priority 3) - Modern frontend using open-design
4. **Code Quality** (Priority 4) - Testing and refactoring
5. **DevOps** (Priority 5) - CI/CD and deployment

Each task includes:
- Clear objectives
- Step-by-step instructions
- Verification criteria
- Dependencies

## Phase 1: Critical Fixes (Priority 1)

### Task 1: Update Kuzu → LadybugDB References

**Objective**: Replace all references to Kuzu with LadybugDB in documentation

**Files to Update**:
1. `spec.md:5.2`
2. `architecture/storage.md`
3. `architecture/identity_graph.md`
4. `decisions/ADR-0001-local-first.md`
5. All other documents containing "Kuzu"

**Implementation Steps**:

1. **Update spec.md**:
   ```bash
   # Read the file
   read /Users/danielkliewer/Documents/Projects/objective06/spec.md
   
   # Replace "Kuzu or Neo4j" with "LadybugDB (default) or Neo4j (enterprise fallback)"
   edit /Users/danielkliewer/Documents/Projects/objective06/spec.md
   oldString: "Kuzu or Neo4j"
   newString: "LadybugDB (default) or Neo4j (enterprise fallback)"
   ```

2. **Update architecture/storage.md**:
   ```bash
   # Add LadybugDB install instructions section
   edit /Users/danielkliewer/Documents/Projects/objective06/architecture/storage.md
   # Add new subsection after "Storage Substrates"
   ```

3. **Update architecture/identity_graph.md**:
   ```bash
   # Find the Failure Modes table
   # Add new row: "Substrate archived upstream — use LadybugDB fork"
   ```

4. **Update decisions/ADR-0001-local-first.md**:
   ```bash
   # Add Revision section at end of file
   # Document the LadybugDB change
   ```

5. **Global consistency pass**:
   ```bash
   # Use grep to find all remaining "Kuzu" references
   grep -r "Kuzu" /Users/danielkliewer/Documents/Projects/objective06 --include="*.md" | grep -v ".git"
   
   # Replace each occurrence with appropriate context
   ```

**Verification**:
- No remaining "Kuzu" references in documentation
- All LadybugDB references include "(default)" where appropriate
- Cross-references between documents are updated

### Task 2: Implement Write Queue for DuckDB

**Objective**: Implement Write Queue to enforce DuckDB single-process constraint

**Implementation Steps**:

1. **Update architecture/orchestration.md**:
   ```bash
   # Add Write Queue component to the architecture diagram
   # Document its purpose and interaction with other components
   ```

2. **Create Write Queue implementation**:
   ```bash
   # Create new file: src/self/orchestrator/write_queue.py
   # Implement:
   # - Bounded queue with priority lanes (HIGH/MEDIUM/LOW)
   # - Serializing UPDATE/DELETE operations
   # - Overflow protection
   # - Integration with DuckDB adapter
   ```

3. **Update DuckDBAdapter**:
   ```bash
   # Modify src/self/storage/duckdb_adapter.py
   # Add queue integration
   # Ensure all writes go through queue
   # Implement queue consumer thread
   ```

**Verification**:
- Write Queue accepts all write operations
- Operations are serialized correctly
- Queue doesn't block read operations
- Performance impact is minimal (<10ms latency)

### Task 3: Complete Three-Layer Prompt Injection Defense

**Objective**: Implement Citation-lock validation (Layer 3)

**Implementation Steps**:

1. **Update architecture/digital_twin.md**:
   ```bash
   # Complete the three-layer model documentation
   # Add detailed explanation of Citation-lock validation
   ```

2. **Implement Citation-lock validation**:
   ```bash
   # Create new file: src/self/digital_twin/prompt_sanitizer.py
   # Implement:
   # - Validation of output citations against declared knowledge
   # - Rejection of outputs referencing undeclared knowledge
   # - Integration with existing sanitization layers
   ```

3. **Update Digital Twin prompt assembly**:
   ```bash
   # Modify src/self/digital_twin/query_intake.py
   # Integrate Citation-lock validation into prompt assembly
   # Ensure validation runs before model invocation
   ```

**Verification**:
- Citation-lock rejects invalid outputs
- Valid outputs pass through
- Performance impact is minimal
- No false positives/negatives

## Phase 2: Documentation Improvements (Priority 2)

### Task 4: Create open-design Project for UI

**Objective**: Set up open-design project for SELF UI design system

**Implementation Steps**:

1. **Create open-design project**:
   ```bash
   # Use open-design tool to create project
   open-design create-project self-ui --name "SELF UI Design System"
   ```

2. **Create component library**:
   ```bash
   # Create base components
   open-design create-artifact self-ui/components/Button.jsx
   open-design create-artifact self-ui/components/Card.jsx
   open-design create-artifact self-ui/components/Input.jsx
   open-design create-artifact self-ui/components/Modal.jsx
   open-design create-artifact self-ui/components/Table.jsx
   open-design create-artifact self-ui/components/Chart.jsx
   open-design create-artifact self-ui/components/Dashboard.jsx
   ```

3. **Create design tokens**:
   ```bash
   # Create theme and design tokens
   open-design create-artifact self-ui/design/Colors.jsx
   open-design create-artifact self-ui/design/Typography.jsx
   open-design create-artifact self-ui/design/Spacing.jsx
   open-design create-artifact self-ui/design/Breakpoints.jsx
   ```

**Verification**:
- Open-design project created successfully
- All components have proper structure
- Design tokens are consistent
- Project is ready for development

### Task 5: Design Component Library (20+ Components)

**Objective**: Create comprehensive component library

**Implementation Steps**:

1. **Core components**:
   ```bash
   # Create 10+ core UI components
   open-design create-artifact self-ui/components/Avatar.jsx
   open-design create-artifact self-ui/components/Badge.jsx
   open-design create-artifact self-ui/components/Breadcrumb.jsx
   open-design create-artifact self-ui/components/Divider.jsx
   open-design create-artifact self-ui/components/Icon.jsx
   open-design create-artifact self-ui/components/Loading.jsx
   open-design create-artifact self-ui/components/Pagination.jsx
   open-design create-artifact self-ui/components/Tabs.jsx
   open-design create-artifact self-ui/components/Tooltip.jsx
   open-design create-artifact self-ui/components/Typography.jsx
   ```

2. **Layout components**:
   ```bash
   # Create layout and container components
   open-design create-artifact self-ui/components/Grid.jsx
   open-design create-artifact self-ui/components/Layout.jsx
   open-design create-artifact self-ui/components/Panel.jsx
   open-design create-artifact self-ui/components/Sidebar.jsx
   ```

3. **Form components**:
   ```bash
   # Create form-related components
   open-design create-artifact self-ui/components/Form.jsx
   open-design create-artifact self-ui/components/Select.jsx
   open-design create-artifact self-ui/components/Checkbox.jsx
   open-design create-artifact self-ui/components/Radio.jsx
   ```

4. **Feedback components**:
   ```bash
   # Create notification and feedback components
   open-design create-artifact self-ui/components/Alert.jsx
   open-design create-artifact self-ui/components/Notification.jsx
   open-design create-artifact self-ui/components/Toast.jsx
   open-design create-artifact self-ui/components/Snackbar.jsx
   ```

**Verification**:
- 20+ components created
- All components follow consistent patterns
- Components are documented
- Components are tested

### Task 6: Create Digital Twin Interface Design

**Objective**: Design conversational interface for Digital Twin

**Implementation Steps**:

1. **Chat interface**:
   ```bash
   # Create chat interface components
   open-design create-artifact self-ui/digital-twin/ChatWindow.jsx
   open-design create-artifact self-ui/digital-twin/MessageList.jsx
   open-design create-artifact self-ui/digital-twin/MessageInput.jsx
   open-design create-artifact self-ui/digital-twin/ConversationHistory.jsx
   ```

2. **Knowledge display**:
   ```bash
   # Create knowledge visualization components
   open-design create-artifact self-ui/digital-twin/KnowledgeGraph.jsx
   open-design create-artifact self-ui/digital-twin/PersonaVector.jsx
   open-design create-artifact self-ui/digital-twin/BeliefsList.jsx
   open-design create-artifact self-ui/digital-twin/Relationships.jsx
   ```

3. **Action panel**:
   ```bash
   # Create action execution interface
   open-design create-artifact self-ui/digital-twin/ActionPanel.jsx
   open-design create-artifact self-ui/digital-twin/ActionHistory.jsx
   open-design create-artifact self-ui/digital-twin/PermissionManager.jsx
   ```

**Verification**:
- All Digital Twin interface components designed
- Interface follows conversational UI principles
- Components are accessible
- Interface is responsive

### Task 7: Design Dashboard and Monitoring Interface

**Objective**: Design real-time monitoring and dashboard interface

**Implementation Steps**:

1. **System health dashboard**:
   ```bash
   # Create system monitoring components
   open-design create-artifact self-ui/dashboard/SystemStatus.jsx
   open-design create-artifact self-ui/dashboard/PerformanceMetrics.jsx
   open-design create-artifact self-ui/dashboard/SubsystemHealth.jsx
   open-design create-artifact self-ui/dashboard/ActivityTimeline.jsx
   ```

2. **Metrics visualization**:
   ```bash
   # Create chart and graph components
   open-design create-artifact self-ui/dashboard/LineChart.jsx
   open-design create-artifact self-ui/dashboard/BarChart.jsx
   open-design create-artifact self-ui/dashboard/PieChart.jsx
   open-design create-artifact self-ui/dashboard/HeatMap.jsx
   ```

3. **Filtering and search**:
   ```bash
   # Create filtering and search components
   open-design create-artifact self-ui/dashboard/FilterPanel.jsx
   open-design create-artifact self-ui/dashboard/DateRangePicker.jsx
   open-design create-artifact self-ui/dashboard/SearchBar.jsx
   ```

**Verification**:
- Dashboard components designed
- Charts and visualizations are functional
- Filtering and search work correctly
- Interface is real-time capable

## Phase 3: Code Quality (Priority 4)

### Task 8: Add Integration Tests

**Objective**: Add integration tests between Observer and Extractor

**Implementation Steps**:

1. **Create integration test directory**:
   ```bash
   # Create test directory
   mkdir -p tests/integration
   
   # Create test configuration
   touch tests/integration/conftest.py
   ```

2. **Create Observer-Extractor integration test**:
   ```bash
   # Create integration test
   cat > tests/integration/test_observer_extractor.py << 'EOF'
   import pytest
   from unittest.mock import Mock, patch
   from self.observer import Observer
   from self.extractor import Extractor
   
   @pytest.fixture
   def mock_observer():
       return Mock(spec=Observer)
   
   @pytest.fixture
   def mock_extractor():
       return Mock(spec=Extractor)
   
   def test_observer_extractor_integration(mock_observer, mock_extractor):
       # Test that Observer events are correctly processed by Extractor
       pass
   
   def test_error_handling():
       # Test error handling between components
       pass
   EOF
   ```

3. **Add security tests**:
   ```bash
   # Create security test suite
   mkdir -p tests/security
   cat > tests/security/test_prompt_injection.py << 'EOF'
   import pytest
   from self.digital_twin.prompt_sanitizer import PromptSanitizer
   
   def test_prompt_injection_sanitizer():
       # Test prompt injection defense
       pass
   ```

**Verification**:
- Integration tests pass
- Security tests pass
- Performance tests pass
- All tests have >80% coverage

### Task 9: Enhance Schema Documentation

**Objective**: Add examples to schema documentation

**Implementation Steps**:

1. **Update observation_event.md**:
   ```bash
   # Add examples for each source adapter
   edit /Users/danielkliewer/Documents/Projects/objective06/schemas/observation_event.md
   # Add Filesystem, Git, GitHub, RSS, Email, Browser, Terminal, Calendar examples
   ```

2. **Update knowledge_object.md**:
   ```bash
   # Add extraction examples
   edit /Users/danielkliewer/Documents/Projects/objective06/schemas/knowledge_object.md
   # Add belief, goal, project, interest examples
   ```

3. **Update identity_node.md**:
   ```bash
   # Add temporal query examples
   edit /Users/danielkliewer/Documents/Projects/objective06/schemas/identity_node.md
   # Add "as of time T" and "during range" examples
   ```

**Verification**:
- All schemas have examples
- Examples are realistic
- Examples cover all use cases
- Documentation is consistent

## Phase 4: DevOps (Priority 5)

### Task 10: Create CI/CD Pipeline

**Objective**: Set up GitHub Actions for automated testing and deployment

**Implementation Steps**:

1. **Create GitHub Actions workflow**:
   ```bash
   # Create .github/workflows directory
   mkdir -p .github/workflows
   
   # Create CI workflow
   cat > .github/workflows/ci.yml << 'EOF'
   name: CI
   
   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.14'
         - name: Install dependencies
           run: pip install -e .
         - name: Run tests
           run: python -m pytest tests/ -v
         - name: Run linting
           run: ruff check .
         - name: Run type checking
           run: mypy src/self/
   EOF
   ```

2. **Create deployment workflow**:
   ```bash
   # Create deployment workflow
   cat > .github/workflows/deploy.yml << 'EOF'
   name: Deploy
   
   on:
     push:
       branches: [main]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Deploy to production
           run: ./scripts/deploy.sh
   EOF
   ```

**Verification**:
- CI pipeline runs successfully
- All tests pass
- Linting and type checking pass
- Deployment workflow works

### Task 11: Add Docker Configuration

**Objective**: Create Docker configuration for production deployment

**Implementation Steps**:

1. **Create Dockerfile**:
   ```bash
   # Create Dockerfile
   cat > Dockerfile << 'EOF'
   FROM python:3.14-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   
   CMD ["python", "-m", "self"]
   EOF
   ```

2. **Create docker-compose**:
   ```bash
   # Create docker-compose for development
   cat > docker-compose.yml << 'EOF'
   version: '3.8'
   
   services:
     self:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - ./data:/app/data
         - ./config:/app/config
       environment:
         - SELF_ENV=production
   EOF
   ```

3. **Create deployment scripts**:
   ```bash
   # Create deployment script
   cat > scripts/deploy.sh << 'EOF'
   #!/bin/bash
   set -e
   
   echo "Deploying SELF..."
   docker-compose down
   docker-compose build
   docker-compose up -d
   
   echo "Deployment complete!"
   EOF
   
   chmod +x scripts/deploy.sh
   ```

**Verification**:
- Docker image builds successfully
- Container runs correctly
- All services start
- Application is accessible

### Task 12: Create Installation Script

**Objective**: Create installation script with first-run wizard

**Implementation Steps**:

```bash
# Create installation script
cat > scripts/install.sh << 'EOF'
#!/bin/bash
set -e

echo "Installing SELF..."

# Check for Python 3.14+
if ! command -v python3 &> /dev/null; then
    echo "Python 3.14+ is required but not installed."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
if [[ $(echo "$python_version < 3.14" | bc -l) -eq 1 ]]; then
    echo "Python 3.14+ is required but found version $python_version."
    exit 1
fi

# Check for Ollama
echo "Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama is required but not installed."
    echo "Please install Ollama from https://ollama.ai"
    exit 1
fi

# Create directories
mkdir -p ~/.config/self
mkdir -p ~/.local/share/self

# Create default config
cat > ~/.config/self/config.yaml << 'CONFIGEOF'
# Default SELF configuration
observer:
  sources:
    - type: filesystem
      path: "~/Documents"
    - type: git
      path: "~/projects"
    - type: github
      token: "[SET_YOUR_TOKEN]"
    - type: rss
      feeds:
        - "https://example.com/feed.xml"
    - type: email
      provider: "gmail"
      credentials_file: "~/.config/self/email_credentials.json"
    - type: browser
      history_file: "~/.config/google-chrome/Default/History"
    - type: terminal
      session_dir: "~/terminal_sessions"
    - type: calendar
      provider: "google"
      credentials_file: "~/.config/self/calendar_credentials.json"

extraction:
  model: "llama3.2"
  max_tokens: 2000
  temperature: 0.1

storage:
  duckdb_path: "~/.local/share/self/self.duckdb"
  vector_db_path: "~/.local/share/self/self_vector.db"

persona_engine:
  embedding_model: "nomic-embed-text"
  update_frequency: "daily"
  decay_rate: 0.95

action_engine:
  sandbox_path: "~/.local/share/self/sandbox"
  max_actions_per_session: 10
  confirmation_required: true

synthesis:
  summary_schedule:
    daily: "08:00"
    weekly: "Monday 08:00"
  summary_types:
    - daily
    - weekly
    - topic
    - project

security:
  enable_prompt_injection_filter: true
  enable_audit_logging: true
  audit_log_path: "~/.local/share/self/audit.log"

# End of config
CONFIGEOF

echo "Configuration created at ~/.config/self/config.yaml"
echo "Please edit the configuration file and set your API tokens."
echo ""
echo "Next steps:"
echo "1. Set up your source adapters (GitHub, email, etc.)"
echo "2. Start Ollama: ollama serve"
echo "3. Run SELF: python -m self"

echo ""
echo "SELF installation complete!"
EOF

chmod +x scripts/install.sh
```

**Verification**:
- Installation script runs successfully
- All checks pass
- Configuration is created
- User is guided through setup

## Implementation Order

### Priority Order:
1. **Critical Fixes** (Tasks 1-3) - Weeks 1-2
2. **UI Design** (Tasks 4-7) - Weeks 3-8
3. **Documentation** (Tasks 8-9) - Weeks 9-10
4. **DevOps** (Tasks 10-12) - Weeks 11-12

### Dependencies:
- Task 1 depends on: Understanding of Kuzu vs LadybugDB
- Task 2 depends on: Understanding of DuckDB constraints
- Task 3 depends on: Understanding of prompt injection defense
- Task 4 depends on: Access to open-design tools
- Task 5 depends on: Task 4 completion
- Task 6 depends on: Task 4 completion
- Task 7 depends on: Task 4 completion
- Task 8 depends on: Understanding of integration testing
- Task 9 depends on: Understanding of schema structure
- Task 10 depends on: Understanding of CI/CD best practices
- Task 11 depends on: Understanding of Docker best practices
- Task 12 depends on: Understanding of installation best practices

## Success Criteria

### Code Quality:
- All tests pass (325+ tests)
- ruff and mypy clean
- 100% test coverage for new code
- No linting errors

### Documentation:
- All architecture documents updated
- All schemas documented with examples
- All evaluations passing
- Cross-references complete

### UI/UX:
- 20+ components created
- All components tested
- Interface accessible (WCAG 2.1 AA)
- Responsive design on all devices

### DevOps:
- CI pipeline automated
- Docker configuration ready
- Deployment scripts working
- Monitoring integrated

## Conclusion

This implementation plan provides a comprehensive roadmap for improving the SELF project. By following these tasks in priority order, the project will achieve production readiness while maintaining its architectural excellence and documentation-first philosophy.

The plan balances:
- **Critical fixes** (security, data integrity)
- **Documentation enhancements** (examples, cross-references)
- **UI/UX improvements** (modern frontend using open-design)
- **Code quality** (integration tests, refactoring)
- **DevOps** (CI/CD, Docker, installation)

Each task includes clear instructions, verification criteria, and dependencies to ensure successful implementation.