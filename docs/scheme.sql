
CREATE TABLE auth0_users (
	id UUID NOT NULL, 
	password_hash VARCHAR(256) NOT NULL, 
	phone VARCHAR(16), 
	email VARCHAR(64), 
	deleted_at DATETIME, 
	email_verified BOOLEAN NOT NULL, 
	phone_verified BOOLEAN NOT NULL, 
	role_id INTEGER, 
	logged_with_provider VARCHAR, 
	provider_id VARCHAR, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT oauth_unique_user_constraint UNIQUE (logged_with_provider, provider_id), 
	UNIQUE (phone), 
	UNIQUE (email)
);
COMMENT ON TABLE auth0_users IS 'Represents a user in the system';
COMMENT ON COLUMN auth0_users.id IS 'Unique identifier for the user';
COMMENT ON COLUMN auth0_users.password_hash IS 'Hashed password of the user';
COMMENT ON COLUMN auth0_users.phone IS 'Phone number of the user';
COMMENT ON COLUMN auth0_users.email IS 'Email address of the user';
COMMENT ON COLUMN auth0_users.deleted_at IS 'Timestamp when the user was deleted';
COMMENT ON COLUMN auth0_users.email_verified IS 'Indicates if the user''s email is verified';
COMMENT ON COLUMN auth0_users.phone_verified IS 'Indicates if the user''s phone is verified';
COMMENT ON COLUMN auth0_users.role_id IS 'Role identifier for the user';
COMMENT ON COLUMN auth0_users.logged_with_provider IS 'OAuth provider used for logging in';
COMMENT ON COLUMN auth0_users.provider_id IS 'Identifier from the OAuth provider';

CREATE TABLE auth0_confirmation_codes (
	id UUID NOT NULL, 
	code VARCHAR(64) NOT NULL, 
	user_id UUID NOT NULL, 
	expired_at DATETIME NOT NULL, 
	used BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES auth0_users (id) ON DELETE CASCADE
);
COMMENT ON TABLE auth0_confirmation_codes IS 'Represents a confirmation code in the system';
COMMENT ON COLUMN auth0_confirmation_codes.id IS 'Unique identifier for the confirmation code';
COMMENT ON COLUMN auth0_confirmation_codes.code IS 'Confirmation code';
COMMENT ON COLUMN auth0_confirmation_codes.user_id IS 'Identifier of the user associated with the confirmation code';
COMMENT ON COLUMN auth0_confirmation_codes.expired_at IS 'Timestamp when the confirmation code expires';
COMMENT ON COLUMN auth0_confirmation_codes.used IS 'Indicates if the confirmation code has been used';

CREATE TABLE auth0_oauth_clients (
	client_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	application_name VARCHAR(20) NOT NULL, 
	client_secret VARCHAR NOT NULL, 
	homepage_url VARCHAR NOT NULL, 
	authorization_callback_url VARCHAR NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (client_id), 
	FOREIGN KEY(user_id) REFERENCES auth0_users (id), 
	UNIQUE (application_name)
);
COMMENT ON TABLE auth0_oauth_clients IS 'Represents an OAuth client in the system';
COMMENT ON COLUMN auth0_oauth_clients.client_id IS 'Unique identifier for the OAuth client';
COMMENT ON COLUMN auth0_oauth_clients.user_id IS 'Identifier of the user associated with the OAuth client';
COMMENT ON COLUMN auth0_oauth_clients.application_name IS 'Name of the application';
COMMENT ON COLUMN auth0_oauth_clients.client_secret IS 'Client secret for the OAuth client';
COMMENT ON COLUMN auth0_oauth_clients.homepage_url IS 'Homepage URL of the OAuth client';
COMMENT ON COLUMN auth0_oauth_clients.authorization_callback_url IS 'Authorization callback URL for the OAuth client';

CREATE TABLE auth0_phone_login_codes (
	id INTEGER NOT NULL, 
	value VARCHAR(6) NOT NULL, 
	user_id UUID NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (value), 
	UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES auth0_users (id)
);
COMMENT ON TABLE auth0_phone_login_codes IS 'Represents a phone login code in the system';
COMMENT ON COLUMN auth0_phone_login_codes.id IS 'Unique identifier for the phone login code';
COMMENT ON COLUMN auth0_phone_login_codes.value IS 'Phone login code';
COMMENT ON COLUMN auth0_phone_login_codes.user_id IS 'Identifier of the user associated with the phone login code';

CREATE TABLE auth0_sessions (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	ip VARCHAR(15) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	is_closed BOOLEAN NOT NULL, 
	auth_token_data JSONB, 
	refresh_token_data JSONB, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES auth0_users (id)
);
COMMENT ON TABLE auth0_sessions IS 'Represents a user session in the system';
COMMENT ON COLUMN auth0_sessions.id IS 'Unique identifier for the session';
COMMENT ON COLUMN auth0_sessions.user_id IS 'Identifier of the user associated with the session';
COMMENT ON COLUMN auth0_sessions.ip IS 'IP address of the session';
COMMENT ON COLUMN auth0_sessions.is_active IS 'Indicates if the session is active';
COMMENT ON COLUMN auth0_sessions.is_closed IS 'Indicates if the session is closed';
COMMENT ON COLUMN auth0_sessions.auth_token_data IS 'Data for the authentication token';
COMMENT ON COLUMN auth0_sessions.refresh_token_data IS 'Data for the refresh token';

CREATE TABLE auth0_oauth_grant_codes (
	id INTEGER NOT NULL, 
	client_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	value VARCHAR(16) NOT NULL, 
	expires DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(client_id) REFERENCES auth0_oauth_clients (client_id), 
	FOREIGN KEY(user_id) REFERENCES auth0_users (id), 
	UNIQUE (value)
);
COMMENT ON TABLE auth0_oauth_grant_codes IS 'Represents an OAuth grant code in the system';
COMMENT ON COLUMN auth0_oauth_grant_codes.id IS 'Unique identifier for the OAuth grant code';
COMMENT ON COLUMN auth0_oauth_grant_codes.client_id IS 'Identifier of the OAuth client';
COMMENT ON COLUMN auth0_oauth_grant_codes.user_id IS 'Identifier of the user associated with the OAuth grant code';
COMMENT ON COLUMN auth0_oauth_grant_codes.value IS 'OAuth grant code';
COMMENT ON COLUMN auth0_oauth_grant_codes.expires IS 'Timestamp when the OAuth grant code expires';
