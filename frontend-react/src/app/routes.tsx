import { createBrowserRouter } from "react-router";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { DashboardLayout } from "./components/DashboardLayout";
import { Overview } from "./pages/Overview";
import { FraudPrediction } from "./pages/FraudPrediction";
import { TransactionRisk } from "./pages/TransactionRisk";
import { MuleGraph } from "./pages/MuleGraph";
import { ModelEngine } from "./pages/ModelEngine";
import { ModelMonitoring } from "./pages/ModelMonitoring";
import { APIConsole } from "./pages/APIConsole";
import { CICD } from "./pages/CICD";
import { Settings } from "./pages/Settings";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: LandingPage,
  },
  {
    path: "/login",
    Component: LoginPage,
  },
  {
    path: "/dashboard",
    Component: DashboardLayout,
    children: [
      { index: true, Component: Overview },
      { path: "fraud-prediction", Component: FraudPrediction },
      { path: "transactions", Component: TransactionRisk },
      { path: "mule-graph", Component: MuleGraph },
      { path: "model-engine", Component: ModelEngine },
      { path: "monitoring", Component: ModelMonitoring },
      { path: "api", Component: APIConsole },
      { path: "cicd", Component: CICD },
      { path: "settings", Component: Settings },
    ],
  },
]);
