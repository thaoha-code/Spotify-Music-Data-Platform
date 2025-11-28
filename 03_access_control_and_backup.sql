--THỰC HIỆN PHÂN QUYỀN CHO ADMIN
-- Bước 1: Tạo Login ở mức Server
CREATE LOGIN admin_login 
WITH PASSWORD = '12345', -- Đặt mật khẩu 
     DEFAULT_DATABASE = SPOTIFY_G11; -- Cơ sở dữ liệu mặc định

-- Bước 2: Tạo User trong cơ sở dữ liệu
USE SPOTIFY_G11;
GO
CREATE USER admin_user 
FOR LOGIN admin_login; -- Liên kết với Login vừa tạo

-- Bước 3: Gán toàn quyền cho Admin
ALTER ROLE db_owner ADD MEMBER admin_user;
GRANT CONTROL ON DATABASE::[SPOTIFY_G11] TO admin_user;

--THỰC HIỆN PHÂN QUYỀN DE
-- Bước 1: Tạo Login ở mức Server
CREATE LOGIN de_login 
WITH PASSWORD = 'de123', -- Đặt mật khẩu 
     DEFAULT_DATABASE = SPOTIFY_G11; -- Cơ sở dữ liệu mặc định
-- Bước 2: Tạo User trong cơ sở dữ liệu
USE SPOTIFY_G11;
GO
CREATE USER de_user 
FOR LOGIN de_login; -- Liên kết với Login vừa tạo
-- Bước 3: Gán quyền cho User
--Cấp quyền ghi cho DE_User
ALTER ROLE db_datawriter ADD MEMBER de_user
ALTER ROLE db_datareader ADD MEMBER de_user; --cấp quyền đọc cho DE_User
-- Cho phép tạo stored procedures trên cơ sở dữ liệu
GRANT CREATE PROCEDURE TO de_user;
-- Cho phép chỉnh sửa và thực thi stored procedures trong schema dbo
GRANT ALTER, EXECUTE ON SCHEMA::dbo TO de_user;
-- Gán quyền CREATE FUNCTION trên cơ sở dữ liệu
GRANT CREATE FUNCTION TO de_user;
--
--THỰC HIỆN PHÂN QUYỀN DA
-- Bước 1: Tạo Login ở mức Server
CREATE LOGIN da_login 
WITH PASSWORD = 'da123', -- Đặt mật khẩu 
     DEFAULT_DATABASE = SPOTIFY_G11; -- Cơ sở dữ liệu mặc định
-- Bước 2: Tạo User trong cơ sở dữ liệu
USE SPOTIFY_G11;
GO
CREATE USER da_user 
FOR LOGIN da_login; -- Liên kết với Login vừa tạo
-- Bước 3: Gán quyền chỉ được truy vấn dữ liệu trên bảng
ALTER ROLE db_datareader ADD MEMBER da_user; --cấp quyền đọc cho DA_User

-- KIỂM TRA PHÂN QUYỀN
--Kiểm tra quyền của user trong cơ sở dữ liệu
SELECT 
    dp.name AS UserName,
    dp.type_desc AS UserType,
    pr.permission_name AS PermissionName,
    pr.state_desc AS PermissionState,
    pr.class_desc AS PermissionClass,
    pr.major_id AS ObjectID,
    o.name AS ObjectName
FROM sys.database_principals dp
LEFT JOIN sys.database_permissions pr
    ON dp.principal_id = pr.grantee_principal_id
LEFT JOIN sys.objects o
    ON pr.major_id = o.object_id
WHERE dp.name IN ('admin_user', 'de_user', 'da_user')
ORDER BY dp.name, pr.permission_name;

--Kiểm tra các role của user
USE SPOTIFY_G11;
GO
SELECT 
    dp.name AS UserName,
    r.name AS RoleName
FROM sys.database_principals dp
JOIN sys.database_role_members drm
    ON dp.principal_id = drm.member_principal_id
JOIN sys.database_principals r
    ON drm.role_principal_id = r.principal_id
WHERE dp.name IN ('admin_user', 'de_user', 'da_user');

--Kiểm tra quyền ở mức Server (Login)
SELECT 
    sp.name AS LoginName,
    sp.type_desc AS LoginType,
    sp.is_disabled AS IsDisabled,
    spr.permission_name AS PermissionName,
    spr.state_desc AS PermissionState
FROM sys.server_principals sp
LEFT JOIN sys.server_permissions spr
    ON sp.principal_id = spr.grantee_principal_id
WHERE sp.name IN ('admin_user', 'de_user', 'da_user');



--THU HỒI QUYỀN
-- Thu hồi quyền cho admin_user
USE SPOTIFY_G11;
GO
-- Xóa khỏi vai trò db_owner
ALTER ROLE db_owner DROP MEMBER admin_user;

-- Thu hồi quyền kiểm soát toàn bộ cơ sở dữ liệu
REVOKE CONTROL ON DATABASE::SPOTIFY_G11 FROM admin_user;

-- Thu hồi quyền cho de_user
USE SPOTIFY_G11;
GO
-- Xóa khỏi các vai trò db_datawriter và db_datareader
ALTER ROLE db_datawriter DROP MEMBER de_user;
ALTER ROLE db_datareader DROP MEMBER de_user;

-- Thu hồi quyền tạo stored procedures
REVOKE CREATE PROCEDURE TO de_user;

-- Thu hồi quyền ALTER và EXECUTE trên schema dbo
REVOKE ALTER, EXECUTE ON SCHEMA::dbo FROM de_user;

-- Thu hồi quyền tạo hàm
REVOKE CREATE FUNCTION TO de_user;


--Thu hồi quyền cho da_user
USE SPOTIFY_G11;
GO
-- Xóa khỏi vai trò db_datareader
ALTER ROLE db_datareader DROP MEMBER da_user;


-- Xóa User khỏi cơ sở dữ liệu
USE SPOTIFY_G11;
GO
DROP USER admin_user;
DROP USER de_user;
DROP USER da_user;

--Xóa Login khỏi Server
DROP LOGIN admin_login;
DROP LOGIN de_login;
DROP LOGIN da_login;


--Kiểm tra quyền của User
SELECT 
    dp.name AS UserName,
    dp.type_desc AS UserType,
    pr.permission_name AS PermissionName,
    pr.state_desc AS PermissionState,
    pr.class_desc AS PermissionClass,
    pr.major_id AS ObjectID,
    o.name AS ObjectName
FROM sys.database_principals dp
LEFT JOIN sys.database_permissions pr
    ON dp.principal_id = pr.grantee_principal_id
LEFT JOIN sys.objects o
    ON pr.major_id = o.object_id
WHERE dp.name IN ('admin_user', 'de_user', 'da_user')
ORDER BY dp.name, pr.permission_name;


--Kiểm tra các vai trò của User
SELECT 
    dp.name AS UserName,
    r.name AS RoleName
FROM sys.database_principals dp
JOIN sys.database_role_members drm
    ON dp.principal_id = drm.member_principal_id
JOIN sys.database_principals r
    ON drm.role_principal_id = r.principal_id
WHERE dp.name IN ('admin_user', 'de_user', 'da_user');

SELECT 
    princ.name AS PrincipalName,
    perm.permission_name AS PermissionName,
    perm.state_desc AS PermissionState,
    CASE 
        WHEN perm.major_id = 0 THEN 'Database Level' 
        ELSE 'Schema/Object Level'
    END AS Scope
FROM 
    sys.database_permissions AS perm
JOIN 
    sys.database_principals AS princ ON perm.grantee_principal_id = princ.principal_id
WHERE 
    princ.name IN ('admin_user', 'de_user', 'da_user')  
ORDER BY 
    PrincipalName, Scope;
