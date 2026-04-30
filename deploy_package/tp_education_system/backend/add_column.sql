-- 添加关联模板ID字段到business_checklist表
ALTER TABLE business_checklist ADD COLUMN IF NOT EXISTS "关联模板ID" VARCHAR(100);

-- 添加注释
COMMENT ON COLUMN business_checklist."关联模板ID" IS '关联的文档模板ID，用于自动跳转到模板填报页面';
