export type RestErrorCode =
  | "BAD_REQUEST"
  | "NOT_FOUND"
  | "TEMPORARILY_BLOCKED"
  | "VALIDATION_ERROR"
  | "RATE_LIMITED"
  | "UPBIT_BAD_REQUEST"
  | "UPBIT_ERROR"
  | "UPBIT_TIMEOUT"
  | "INTERNAL_ERROR";

export type WebSocketErrorCode =
  | "INVALID_MESSAGE"
  | "UNSUPPORTED_MESSAGE_TYPE"
  | "INVALID_MARKET"
  | "BAD_REQUEST"
  | "VALIDATION_ERROR"
  | "RATE_LIMITED"
  | "TEMPORARILY_BLOCKED"
  | "UPBIT_WS_ERROR"
  | "INTERNAL_ERROR";

export type ErrorData = {
  code: RestErrorCode | WebSocketErrorCode;
  message: string;
  details?: Record<string, unknown> | null;
};

export type ErrorEnvelope = {
  type: "error";
  timestamp: string;
  data: ErrorData;
};
