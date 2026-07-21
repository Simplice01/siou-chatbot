-- Données de référence minimales SIOU.
-- À exécuter après schema.sql.

BEGIN;

INSERT INTO organizations (name, acronym, type, description, country, city, email, phone)
VALUES
  (
    'Ministère de la Transformation Digitale et de l''Innovation',
    'MTDI',
    'ministere',
    'Ministère porteur du système SIOU et responsable de la gouvernance globale de la base de connaissances.',
    'Bénin',
    'Cotonou',
    'accueil@mtdi.test',
    '+229 01 90 00 10 10'
  )
ON CONFLICT (acronym) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  updated_at = now();

WITH mtdi AS (
  SELECT id FROM organizations WHERE acronym = 'MTDI'
)
INSERT INTO organizations (parent_id, name, acronym, type, description, missions, city, country, email, phone)
SELECT mtdi.id, item.name, item.acronym, item.type::organization_type, item.description, item.missions, 'Cotonou', 'Bénin', item.email, item.phone
FROM mtdi,
(VALUES
  (
    'Direction du Numérique',
    'DN',
    'direction',
    'Direction chargée de la coordination des politiques publiques de transformation digitale.',
    'Orientation stratégique des projets numériques publics, coordination sectorielle et appui aux politiques numériques.',
    'direction.numerique@mtdi.test',
    '+229 01 90 00 11 01'
  ),
  (
    'Agence des Systèmes d''Information et du Numérique',
    'ASIN',
    'agence',
    'Agence issue de la fusion de plusieurs structures numériques, citée par le décret 2022-324.',
    'Systèmes d''information publics, cybersécurité institutionnelle, plateformes numériques et infrastructure.',
    'contact@asin.test',
    '+229 01 90 00 12 02'
  ),
  (
    'Société Béninoise d''Infrastructures Numériques',
    'SBIN',
    'societe',
    'Société concernée par les infrastructures numériques et services de connectivité, citée par le décret 2018-552.',
    'Services de connectivité, réseau, infrastructures numériques et offres télécom.',
    'contact@sbin.test',
    '+229 01 90 00 14 04'
  ),
  (
    'Guichet Startup',
    'GUICHET_STARTUP',
    'guichet',
    'Point d''orientation pour les demandes relatives au label Startup et à l''accompagnement des startups numériques.',
    'Informer sur le label Startup, les pièces à fournir, l''éligibilité et les dispositifs d''accompagnement.',
    'startup@mtdi.test',
    '+229 01 90 00 15 05'
  ),
  (
    'Cellule protection des données',
    'CPD',
    'cellule',
    'Cellule d''orientation pour les questions de données personnelles et de confidentialité.',
    'Conseil sur la conservation des données, la proportionnalité, la confidentialité et les obligations de protection.',
    'donnees.personnelles@mtdi.test',
    '+229 01 90 00 17 07'
  ),
  (
    'Équipe support SIOU',
    'SUPPORT_SIOU',
    'service',
    'Service chargé des signalements, corrections et problèmes d''indexation liés à SIOU.',
    'Recevoir les signalements d''erreurs, coordonner les corrections et alimenter la gouvernance documentaire.',
    'support-siou@mtdi.test',
    NULL
  )
) AS item(name, acronym, type, description, missions, email, phone)
ON CONFLICT (acronym) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  missions = EXCLUDED.missions,
  email = EXCLUDED.email,
  phone = EXCLUDED.phone,
  updated_at = now();

INSERT INTO service_cards (
  organization_id,
  title,
  public_name,
  target_users,
  orientation_summary,
  procedure_summary,
  requirements,
  contacts,
  keywords,
  status,
  last_reviewed_at,
  next_review_at
)
SELECT
  organizations.id,
  item.title,
  item.public_name,
  item.target_users,
  item.orientation_summary,
  item.procedure_summary,
  item.requirements::jsonb,
  item.contacts::jsonb,
  item.keywords,
  'publie',
  now(),
  now() + interval '30 days'
FROM organizations
JOIN (
  VALUES
  (
    'GUICHET_STARTUP',
    'Orientation label Startup',
    'Label Startup',
    'Entrepreneurs, startups, porteurs de projets numériques',
    'Orienter l''usager vers le Guichet Startup pour vérifier son éligibilité et obtenir les pièces requises.',
    'L''usager prépare une description du projet, les statuts, les informations sur l''équipe et contacte le guichet.',
    '["description du projet", "statuts", "informations sur l''équipe"]',
    '[{"type":"email","value":"startup@mtdi.test"},{"type":"phone","value":"+229 01 90 00 15 05"}]',
    ARRAY['startup', 'label', 'innovation', 'entrepreneur']::TEXT[]
  ),
  (
    'ASIN',
    'Signalement incident cybersécurité',
    'Incident cybersécurité',
    'Administrations, agents publics, responsables SI',
    'Orienter vers l''ASIN lorsqu''un incident touche une plateforme publique ou un système d''information institutionnel.',
    'Décrire l''incident, l''heure observée et le service affecté, sans transmettre de mot de passe.',
    '["description de l''incident", "heure observée", "service affecté"]',
    '[{"type":"email","value":"contact@asin.test"},{"type":"phone","value":"+229 01 90 00 12 02"}]',
    ARRAY['cybersécurité', 'incident', 'plateforme publique', 'ASIN']::TEXT[]
  )
) AS item(acronym, title, public_name, target_users, orientation_summary, procedure_summary, requirements, contacts, keywords)
ON organizations.acronym = item.acronym
ON CONFLICT DO NOTHING;

COMMIT;

