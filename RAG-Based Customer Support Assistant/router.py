from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RouteDecision:
    route: str
    confidence: float
    reason: str


class QueryRouter:
    def decide(self, question: str) -> RouteDecision:
        text = question.lower()

        escalation_terms = {"fraud", "legal", "lawsuit", "chargeback", "complaint", "vip"}
        account_terms = {"account", "password", "login", "sign up", "email", "delete"}
        billing_terms = {"payment", "charged", "invoice", "billing", "refund", "return"}
        order_terms = {"order", "track", "tracking", "delivery", "delayed", "shipping", "address"}
        technical_terms = {"app", "website", "slow", "loading", "browser", "cache", "emails"}

        if any(term in text for term in escalation_terms):
            return RouteDecision("escalate", 0.95, "Sensitive customer issue needs human review")
        if any(term in text for term in order_terms):
            return RouteDecision("orders_delivery", 0.90, "Order or delivery support query")
        if any(term in text for term in billing_terms):
            return RouteDecision("billing_payments", 0.88, "Billing, refund, or payment support query")
        if any(term in text for term in account_terms):
            return RouteDecision("account_management", 0.86, "Account management support query")
        if any(term in text for term in technical_terms):
            return RouteDecision("technical_support", 0.84, "Technical troubleshooting query")
        if len(text.split()) < 3:
            return RouteDecision("needs_clarification", 0.40, "Question is too short for reliable retrieval")
        return RouteDecision("general_customer_support", 0.70, "General customer support query")
