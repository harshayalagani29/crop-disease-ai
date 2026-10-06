create table farmers (
  id uuid primary key default gen_random_uuid(),
  name text not null, location text, language text default 'en',
  farm_size numeric, created_at timestamptz default now()
);
create table crops (
  id uuid primary key default gen_random_uuid(),
  farmer_id uuid references farmers(id) on delete cascade,
  crop_name text not null, sowing_date date, crop_stage text
);
create table disease_predictions (
  id uuid primary key default gen_random_uuid(),
  farmer_id uuid references farmers(id) on delete cascade,
  crop text, image_url text, disease text, confidence numeric,
  risk text, prediction_date timestamptz default now()
);
create table recommendations (
  id uuid primary key default gen_random_uuid(),
  prediction_id uuid references disease_predictions(id) on delete cascade,
  recommendation text, created_at timestamptz default now()
);
