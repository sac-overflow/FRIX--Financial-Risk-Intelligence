import { API_BASE_URL } from "../config/apiConfig";

export interface FraudPredictionRequest {
  amount: number;
  transaction_type: string;
  oldbalanceOrg: number;
  newbalanceOrig: number;
  oldbalanceDest: number;
  newbalanceDest: number;
  sender_txn_count: number;
  receiver_txn_count: number;
}

export interface FraudReasonCodes {
  high_risk_transaction_type: boolean;
  sender_emptied_account: boolean;
  large_amount: boolean;
  origin_balance_error: number;
  dest_balance_error: number;
}

export interface FraudPredictionResponse {
  fraud_prediction: number;
  fraud_probability: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  risk_score_v1: number;
  model_used: string;
  reason_codes: FraudReasonCodes;
}

export async function predictFraud(
  payload: FraudPredictionRequest
): Promise<FraudPredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/predict-fraud`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Fraud prediction failed: ${errorText}`);
  }

  return response.json();
}