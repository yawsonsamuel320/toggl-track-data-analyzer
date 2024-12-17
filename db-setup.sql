CREATE TABLE `organizations` (
  `id` integer PRIMARY KEY,
  `name` varchar(255),
  `created_at` datetime
);

CREATE TABLE `groups` (
  `id` integer PRIMARY KEY,
  `organization_id` integer,
  `name` varchar(255),
  `created_at` datetime
);

CREATE TABLE `workspaces` (
  `id` integer PRIMARY KEY,
  `group_id` integer,
  `name` varchar(255),
  `created_at` datetime
);

CREATE TABLE `clients` (
  `id` integer PRIMARY KEY,
  `organization_id` integer,
  `name` varchar(255),
  `created_at` datetime
);

CREATE TABLE `tasks` (
  `id` integer PRIMARY KEY,
  `project_id` integer,
  `name` varchar(255),
  `description` text,
  `status` varchar(255),
  `created_at` datetime,
  `updated_at` datetime
);

CREATE TABLE `approvals` (
  `id` integer PRIMARY KEY,
  `task_id` integer,
  `approver_id` integer,
  `status` varchar(255),
  `created_at` datetime
);

CREATE TABLE `users` (
  `id` integer PRIMARY KEY,
  `name` varchar(255),
  `email` varchar(255) UNIQUE,
  `created_at` datetime
);

CREATE TABLE `projects` (
  `id` integer PRIMARY KEY,
  `client_id` integer,
  `name` varchar(255),
  `created_at` datetime,
  `updated_at` datetime
);

CREATE TABLE `time_entries` (
  `id` integer PRIMARY KEY,
  `user_id` integer,
  `project_id` integer,
  `description` text,
  `start_time` datetime,
  `end_time` datetime,
  `duration` integer,
  `created_at` datetime
);

ALTER TABLE `groups` ADD FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

ALTER TABLE `workspaces` ADD FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`);

ALTER TABLE `clients` ADD FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

ALTER TABLE `tasks` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `approvals` ADD FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`);

ALTER TABLE `approvals` ADD FOREIGN KEY (`approver_id`) REFERENCES `users` (`id`);

ALTER TABLE `projects` ADD FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`);

ALTER TABLE `time_entries` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `time_entries` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);
