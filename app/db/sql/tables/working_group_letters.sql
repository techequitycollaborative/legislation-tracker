-- wg_letters.sql
-- Get MOST RECENT letters from all organizations for a bill on the working group dashboard


-- Create the new table with the most recent letters for each bill/org combination
DROP TABLE IF EXISTS app.wg_dashboard_letters;

CREATE TABLE app.wg_dashboard_letters AS
SELECT DISTINCT ON (wgd.openstates_bill_id, blh.org_id)
    wgd.openstates_bill_id,
    wgd.bill_number,
    blh.org_id,
    blh.org_name,
    blh.letter_name,
    blh.letter_url,
	blh.created_on,
    blh.created_at
FROM app.working_group_dashboard wgd
INNER JOIN app.bill_letter_history blh 
    ON wgd.openstates_bill_id = blh.openstates_bill_id
ORDER BY wgd.openstates_bill_id, blh.org_id, blh.created_at DESC;

-- Add indexes for better query performance
CREATE INDEX idx_wg_dashboard_letters_bill ON app.wg_dashboard_letters(openstates_bill_id);
CREATE INDEX idx_wg_dashboard_letters_org ON app.wg_dashboard_letters(org_id);
CREATE INDEX idx_wg_dashboard_letters_bill_org ON app.wg_dashboard_letters(openstates_bill_id, org_id);