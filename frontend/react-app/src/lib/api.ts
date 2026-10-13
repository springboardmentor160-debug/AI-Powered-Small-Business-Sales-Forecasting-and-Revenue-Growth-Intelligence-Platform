const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export type UserRole =
  | "business_owner"
  | "store_manager"
  | "sales_executive"
  | "admin";

export type PublicRegistrationRole =
  | "business_owner"
  | "store_manager"
  | "sales_executive";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  role: UserRole;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  role: PublicRegistrationRole;
}

export interface RegisterResponse {
  message: string;
  email: string;
  role: UserRole;
}

export interface SalesSummary {
  status: string;
  total_revenue: number;
  total_orders: number;
  top_product: string;
}

export interface ApiError {
  detail?: string;
  message?: string;
}

export class ApiRequestError extends Error {
  public readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers = new Headers(options.headers);

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch {
    throw new ApiRequestError(
      "Cannot connect to MarketMindAI. Check that the backend is running.",
      0,
    );
  }

  if (!response.ok) {
    let message = `Request failed (${response.status}).`;

    try {
      const body = (await response.json()) as ApiError;

      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (typeof body.message === "string") {
        message = body.message;
      }
    } catch {
      // Keep the HTTP status message when the response is not JSON.
    }

    throw new ApiRequestError(message, response.status);
  }

  return (await response.json()) as T;
}

export function login(
  credentials: LoginRequest,
): Promise<LoginResponse> {
  return apiRequest<LoginResponse>("/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export function register(
  details: RegisterRequest,
): Promise<RegisterResponse> {
  return apiRequest<RegisterResponse>("/register", {
    method: "POST",
    body: JSON.stringify(details),
  });
}

export function getHealth(): Promise<{
  status: string;
  service: string;
  version: string;
}> {
  return apiRequest("/health");
}

export function getSalesSummary(
  token: string,
): Promise<SalesSummary> {
  return apiRequest<SalesSummary>("/sales/summary", {}, token);
}

/* Forecasting */

export interface ForecastModel {
  model: string;
  mae: number;
  rmse: number;
  [key: string]: unknown;
}

export interface DemandPrediction {
  date?: string;
  actual_units?: number;
  predicted_units?: number;
  [key: string]: unknown;
}

export interface RevenuePrediction {
  date?: string;
  actual_revenue?: number;
  prophet_prediction?: number;
  random_forest_prediction?: number;
  xgboost_prediction?: number;
  [key: string]: unknown;
}

export interface DemandForecast {
  status: string;
  feature: string;
  validation_horizon_days: number;
  validation_start: string | null;
  validation_end: string | null;
  models: ForecastModel[];
  predictions?: DemandPrediction[];
}

export interface RevenueForecast {
  status: string;
  feature: string;
  validation: {
    test_split?: string;
    test_start?: string;
    test_end?: string;
    test_rows?: number;
  };
  models: ForecastModel[];
  predictions?: RevenuePrediction[];
}

export interface ForecastModelComparison {
  status: string;
  uci_revenue_models: ForecastModel[];
  m5_demand_models: ForecastModel[];
}

export function getDemandForecast(
  token: string,
): Promise<DemandForecast> {
  return apiRequest<DemandForecast>("/forecast/demand", {}, token);
}

export function getRevenueForecast(
  token: string,
): Promise<RevenueForecast> {
  return apiRequest<RevenueForecast>("/forecast/revenue", {}, token);
}

export function getForecastModelComparison(
  token: string,
): Promise<ForecastModelComparison> {
  return apiRequest<ForecastModelComparison>(
    "/forecast/models",
    {},
    token,
  );
}

/* Customer segmentation */

export interface SegmentSummary {
  segment: string;
  customer_count: number;
  average_purchase_frequency: number;
  average_purchase_value: number;
  average_customer_activity_days: number;
}

export interface SegmentedCustomer {
  "Customer ID": string | number | null;
  purchase_frequency: number | null;
  purchase_value: number | null;
  last_purchase_date: string | null;
  customer_activity_days: number | null;
  cluster: number | string | null;
  cluster_hierarchical: number | string | null;
  segment_name: string | null;
}

export interface CustomerSegments {
  status: string;
  feature: string;
  total_customers: number;
  segment_count: number;
  segment_summary: SegmentSummary[];
  customers: SegmentedCustomer[];
}

export function getCustomerSegments(
  token: string,
): Promise<CustomerSegments> {
  return apiRequest<CustomerSegments>("/segments", {}, token);
}

/* Invoices */

export type PaymentStatus = "Pending" | "Paid" | "Cancelled";

export interface InvoiceRecord {
  invoice_id: string;
  customer_name: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_amount: number;
  payment_status: PaymentStatus;
  created_by: string;
  created_at: string;
}

export interface InvoiceListResponse {
  status: string;
  mode: string;
  message: string;
  total_invoices: number;
  invoices: InvoiceRecord[];
}

export interface InvoiceCreateRequest {
  customer_name: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  payment_status: PaymentStatus;
}

export interface InvoiceCreateResponse {
  status: string;
  mode: string;
  message: string;
  invoice: InvoiceRecord;
}

export function getInvoices(
  token: string,
): Promise<InvoiceListResponse> {
  return apiRequest<InvoiceListResponse>("/invoices/view", {}, token);
}

export function createInvoice(
  details: InvoiceCreateRequest,
  token: string,
): Promise<InvoiceCreateResponse> {
  return apiRequest<InvoiceCreateResponse>(
    "/invoices/create",
    {
      method: "POST",
      body: JSON.stringify(details),
    },
    token,
  );
}

/* Inventory */

export interface InventoryProduct {
  ProductID: string;
  ProductDescription: string;
  TotalUnitsSold: number;
  InitialStock: number;
  EstimatedRemainingStock: number;
}

export interface InventoryPreview {
  message: string;
  source_files: string[];
  inventory_method: string;
  note: string;
  total_products: number;
  total_units_sold: number;
  total_estimated_initial_stock: number;
  total_estimated_remaining_stock: number;
  products: InventoryProduct[];
}

export function getInventoryPreview(
  token: string,
): Promise<InventoryPreview> {
  return apiRequest<InventoryPreview>(
    "/inventory/preview",
    {},
    token,
  );
}

/* Administration */

export interface AdminUsersResponse {
  status: string;
  feature: string;
  registered_user_profiles: string[];
}

export function getAdminUsers(
  token: string,
): Promise<AdminUsersResponse> {
  return apiRequest<AdminUsersResponse>("/admin/users", {}, token);
}