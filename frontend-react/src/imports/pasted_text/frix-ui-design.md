Design a premium, minimalistic SaaS web platform UI for “FRIX — Financial Risk Intelligence”, a fintech fraud detection, mule-risk, AML-style risk intelligence, and adaptive ML model monitoring platform.

Overall design direction:
Create a high-end Apple-inspired fintech interface with a monochromatic color palette: deep charcoal, black, off-white, soft greys, graphite surfaces, and subtle glass-like depth. Use controlled accent glows only where needed: blue glow for intelligence/AI/low-risk confidence, red glow for fraud/high-risk alerts. The design should feel premium, sharp, clean, futuristic, and enterprise-ready. Avoid colorful dashboards. Avoid playful rounded UI. Use mostly sharp-edged cards and buttons, but slight micro-radius is acceptable similar to ChatGPT conversation cards. The UI should feel like a serious financial risk command center.

Brand style:

* Product name: FRIX
* Full form: Financial Risk Intelligence
* Tone: premium, secure, intelligent, minimal
* Style references: Apple website minimalism, OpenAI/ChatGPT clean cards, Stripe-style SaaS polish, Bloomberg-level seriousness but modernized
* Use dark mode first, but design should be adaptable to light mode later
* Fonts should be modern, clean, and premium, similar to SF Pro / Inter / Neue Haas Grotesk style
* Use strong spacing, hierarchy, and subtle transitions

Core product concept:
FRIX is a fraud-risk intelligence platform that detects suspicious financial transactions using rule-based scoring, ML models, graph/mule-risk features, model comparison, API inference, CI/CD-ready deployment, and future adaptive model selection. The platform should visually support current and future capabilities.

Create a full product layout with these pages and sections:

1. Landing / Product Overview Page
   Hero section:

* Large title: “Financial Risk Intelligence, engineered for modern fraud detection.”
* Subtitle: “Detect fraud, expose mule-risk patterns, compare ML models, and operationalize real-time risk decisions from one intelligent platform.”
* CTA buttons: “Open Risk Console” and “View Model Engine”
* Hero visual: abstract transaction network graph, glowing risk nodes, fraud signal pulses, and a clean risk score card overlay
* Use subtle red glow for high-risk nodes and blue glow for AI intelligence layer
* Add quick stats cards:

  * “Real-time Fraud Scoring”
  * “Graph Mule-Risk Layer”
  * “Adaptive Model Engine”
  * “CI/CD + Docker Ready”

2. Login Page
   Create a premium minimal login screen:

* FRIX logo/title at top
* Left side: subtle abstract fraud-network visual
* Right side: login card with sharp edges
* Fields: Email, Password
* Buttons: “Sign in”, “Continue with GitHub”
* Small links: “Forgot password?”, “Request enterprise access”
* Use monochrome surfaces with blue glow on active input and red glow only for validation error state

3. Main Dashboard Page
   Create a full SaaS dashboard layout:

* Left sidebar navigation with sections:

  * Overview
  * Transaction Risk
  * Fraud Prediction
  * Mule Graph
  * Model Engine
  * Model Monitoring
  * API Console
  * CI/CD & Deployment
  * Settings
* Top bar:

  * Search transactions
  * Environment selector: Local / Staging / Production
  * User avatar
  * Notification icon
* Dashboard cards:

  * Total Transactions Scored
  * Fraud Alerts
  * High Risk Value
  * False Positive Watch
  * Active Model
  * API Health
* Add a large “Risk Activity Timeline” chart
* Add a “Fraud Probability Distribution” chart
* Add a “Recent High-Risk Transactions” table
* Add small status pill: “FastAPI Service: Healthy”
* Use blue glow for healthy/active states, red glow for high-risk alert counts

4. Fraud Prediction Console
   Design a page where a user can submit or inspect a transaction:

* Form/card for transaction input:

  * amount
  * transaction_type
  * oldbalanceOrg
  * newbalanceOrig
  * oldbalanceDest
  * newbalanceDest
  * sender_txn_count
  * receiver_txn_count
* Button: “Run Fraud Prediction”
* Output card:

  * fraud_prediction
  * fraud_probability
  * risk_level
  * risk_score_v1
  * model_used
* Reason codes panel:

  * high_risk_transaction_type
  * sender_emptied_account
  * large_amount
  * origin_balance_error
  * dest_balance_error
* Add a visual risk meter from LOW to HIGH using monochrome base with blue to red glow highlights

5. Transaction Risk Page
   Create a clean data table and filtering interface:

* Table columns:

  * Transaction ID
  * Type
  * Amount
  * Sender
  * Receiver
  * Fraud Probability
  * Risk Level
  * Model Used
  * Reason Codes
  * Timestamp
* Filters:

  * Risk Level
  * Transaction Type
  * Model
  * Amount Range
  * Alert Status
* Add row states:

  * Low risk = subtle blue/grey
  * Medium risk = neutral warning glow
  * High risk = red edge glow
* Keep table minimal and enterprise-looking

6. Mule Graph / Network Risk Page
   Create a graph analytics page:

* Main visual: account transaction network graph with nodes and edges
* Red glowing nodes for suspicious receivers/mule candidates
* Blue nodes for normal accounts
* Side panel:

  * receiver_in_degree
  * sender_out_degree
  * receiver_total_amount
  * receiver_avg_amount
  * mule_risk_score_v1
  * mule_alert_v1
* Add “Graph Insight Summary” card:

  * “Potential mule receiver behavior detected”
  * “High-risk transaction concentration”
  * “Network exposure score”
* Use smooth hover interactions on graph nodes

7. Adaptive Model Engine Page
   This is important. Create a future-ready model selection console.
   Show cards for multiple model modes:

* Random Forest Baseline
* XGBoost Advanced Fraud Model
* LightGBM Fast Inference Model
* Graph-Risk Model
* Rule-Assisted Mode
* Explainability-First Mode
* Low-Latency Mode
* High-Accuracy Mode

Create a “Model Selector” panel:

* Client Usage Pattern
* Data Volume
* Required Latency
* Required Accuracy
* Explainability Need
* Volatility Level
* Recommended Model Mode

Add comparison table:

* Model
* Precision
* Recall
* PR-AUC
* False Positives
* False Negatives
* Inference Speed
* Deployment Status

Add a champion/challenger visual:

* Champion Model: Random Forest
* Challenger Models: XGBoost, LightGBM, Graph Risk
* Button: “Promote Champion”
* Button: “Run Benchmark”

8. Model Monitoring Page
   Design MLOps monitoring page:

* Model drift card
* Data drift card
* Prediction volume trend
* Fraud rate trend
* False positive trend
* Latency chart
* API error rate chart
* Active model version
* Last training date
* Last validation score
* Add alert cards for:

  * Drift detected
  * Risk threshold breach
  * Model performance degradation
* Keep it clean and technical

9. API Console Page
   Create an API developer page:

* Endpoint cards:

  * GET /
  * GET /health
  * POST /predict-fraud
* Request sample block
* Response sample block
* API status card
* Docker status card
* CI status card
* Button: “Copy cURL”
* Button: “Open Swagger Docs”
* Add a clean code-block visual with monospace font

10. CI/CD & Deployment Page
    Create a deployment readiness page:

* GitHub Actions status: Passed
* pytest status: 3 tests passed
* Docker image: frix-fastapi
* Container status: Healthy
* Deployment pipeline visual:
  Push to GitHub → Run Tests → Build Docker Image → Push Image → Deploy Service
* Use green/blue glow for passing pipeline steps
* Use red only for failed step states
* Cards:

  * CI Pipeline
  * Docker Build
  * Test Coverage
  * Deployment Target
  * Model Artifact Strategy

11. Settings Page
    Create account and platform settings:

* Workspace settings
* Model preferences
* Risk thresholds
* API keys
* Environment variables
* Notification preferences
* Role-based access placeholder
* Audit logs placeholder

Interaction and motion requirements:

* Smooth page transitions
* Subtle hover elevation on cards
* Sharp buttons with glow border on hover
* Sidebar active state with soft blue glow
* High-risk cards should pulse very subtly with red edge glow
* Graph nodes should animate softly
* Avoid heavy cartoon animations; keep it refined and premium
* Use responsive desktop-first design, but ensure tablet and mobile layouts are considered

Visual style details:

* Background: black/charcoal with soft gradient haze
* Cards: dark graphite, slight glass depth, thin borders
* Buttons: sharp-edged, high contrast, minimal
* Primary CTA: black/white with blue glow
* Danger states: red glow, not full red blocks
* Typography: large clean headings, small muted captions, clean numeric cards
* Icons: thin-line icons only
* Layout should feel spacious, expensive, and professional

Deliverables:
Create desktop screens for:

1. Landing / Overview
2. Login
3. Main Dashboard
4. Fraud Prediction Console
5. Transaction Risk Table
6. Mule Graph
7. Adaptive Model Engine
8. Model Monitoring
9. API Console
10. CI/CD & Deployment
11. Settings

Make the design cohesive as one SaaS product. Use realistic placeholder data based on fraud detection, model performance, API health, and transaction risk. The final output should look like a premium fintech AI platform ready for enterprise demos.
