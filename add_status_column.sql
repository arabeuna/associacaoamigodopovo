-- Script para adicionar a coluna status à tabela presencas
-- Execute este script no PostgreSQL

-- Verificar se a coluna status já existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'presencas' AND column_name = 'status'
    ) THEN
        -- Adicionar a coluna status
        ALTER TABLE presencas ADD COLUMN status VARCHAR(10) CHECK (status IN ('P', 'F', 'J'));
        RAISE NOTICE 'Coluna status adicionada com sucesso';
    ELSE
        RAISE NOTICE 'Coluna status já existe';
    END IF;
END $$;

-- Verificar se a coluna tipo_registro já existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'presencas' AND column_name = 'tipo_registro'
    ) THEN
        -- Adicionar a coluna tipo_registro
        ALTER TABLE presencas ADD COLUMN tipo_registro VARCHAR(20) DEFAULT 'MANUAL';
        RAISE NOTICE 'Coluna tipo_registro adicionada com sucesso';
    ELSE
        RAISE NOTICE 'Coluna tipo_registro já existe';
    END IF;
END $$;

-- Mostrar a estrutura final da tabela
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'presencas'
ORDER BY ordinal_position;
