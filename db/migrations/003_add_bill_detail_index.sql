-- =============================================================================
-- Migration: Add composite index on (openstates_bill_id, last_updated_org_id)
-- Run once against legtracker_2026 to optimize org dashboard queries that join bill_custom_details.
-- =============================================================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bill_custom_details_bill_org
ON app.bill_custom_details (openstates_bill_id, last_updated_org_id);


-- =============================================================================
-- Rollback:
-- DROP INDEX CONCURRENTLY IF EXISTS idx_bill_custom_details_bill_org;
-- =============================================================================