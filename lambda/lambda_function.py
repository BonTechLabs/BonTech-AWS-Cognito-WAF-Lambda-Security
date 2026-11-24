"""Cognito pre-sign-up handler transcribed from the BonTech lab code screenshot.

This validates example email attributes; it does not check geographic origin.
"""
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Read the email supplied during registration
    attributes = event.get("request", {}).get("userAttributes", {})
    email = attributes.get("email", "").strip().lower()

    # Reject missing email addresses
    if not email:
        logger.warning("Registration rejected: missing email")
        raise ValueError("Email address is required")

    # Reject registrations from our test-blocked domain
    if email.endswith("@blocked.example"):
        logger.warning("Registration rejected: blocked domain")
        raise ValueError("Registration is not permitted")

    # Allow Cognito to continue registration
    logger.info("Registration passed custom validation")
    return event
