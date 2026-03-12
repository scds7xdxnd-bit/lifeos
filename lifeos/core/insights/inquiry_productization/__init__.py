"""Inquiry productization layer exports."""

from lifeos.core.insights.inquiry_productization.pipeline import (
    ANSWERABILITY_CLASSES,
    ProductizedInquiryBrief,
    productize_inquiry_brief,
)

__all__ = ["ANSWERABILITY_CLASSES", "ProductizedInquiryBrief", "productize_inquiry_brief"]
