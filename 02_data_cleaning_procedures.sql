USE msdb;
GO
--FULL BACKUP
-- Tạo Job cho Full Backup
EXEC sp_add_job 
    @job_name = 'Full_Backup_Job', --Tên job
    @enabled = 1, 
    @description = 'Job to perform Full Backup every weekend at 00:00'; --Mô tả Job
GO

-- Tạo bước cho Full Backup
EXEC sp_add_jobstep 
    @job_name = 'Full_Backup_Job', --Liên kết bước với Job `Full_Backup_Job`
    @step_name = 'Full Backup Step',--Tên bước
    @subsystem = 'TSQL', 
	@command = 'BACKUP DATABASE Spotify_Group11 TO DISK = ''D:\Backup\Spotify_Group11_Full_'' + CONVERT(NVARCHAR, GETDATE(), 112) + ''_'' + CONVERT(NVARCHAR, GETDATE(), 108) + ''.bak'' WITH FULL, INIT, FORMAT;',  -- Lệnh sao lưu đầy đủ
    @database_name = 'Spotify_Group11', --Database cần sao lưu
    @on_success_action = 1, -- Next Step
    @on_fail_action = 2; -- Quit Job
GO

-- Tạo lịch trình cho Full Backup (Chạy vào Chủ Nhật và Thứ Bảy lúc 00:00)
EXEC sp_add_schedule 
    @schedule_name = 'Full_Backup_Schedule', --Tên lịch
    @enabled = 1, --Bật lịch trình
    @freq_type = 8, -- Weekly
    @freq_interval = 1, -- Sunday (1) 
	@freq_recurrence_factor = 1, -- một tuần 1 lần
    @active_start_time = 000000; -- Thời gian bắt đầu 00:00:00
GO

-- Gắn lịch trình `Full_Backup_Schedule` vào Job `Full_Backup_Job`
EXEC sp_attach_schedule 
    @job_name = 'Full_Backup_Job', --Tên job
    @schedule_name = 'Full_Backup_Schedule'; --Tên lịch trình
GO

-- Liên kết Job `Full_Backup_Job` với SQL Server Agent
EXEC sp_add_jobserver 
    @job_name = 'Full_Backup_Job',  --Tên job
    @server_name = 'LAPTOP-HFTOHS8V'; --Tên Server
GO
-- Xóa các bản sao lưu cũ hơn 7 ngày trong Full Backup Job
EXEC sp_add_jobstep 
    @job_name = 'Full_Backup_Job', --Tên job
    @step_name = 'Delete Old Full Backups', --Tên bước
    @subsystem = 'TSQL', 
    @command = '
        DECLARE @filePath NVARCHAR(255);
        DECLARE @sqlCommand NVARCHAR(MAX);
        
        -- Set backup directory
        SET @filePath = ''D:\Backup\Spotify_Group11_Full_''; 
        
        -- Xóa các file sao lưu cũ hơn 7 ngày
        SET @sqlCommand = ''EXEC xp_delete_file 0, '''' + @filePath + '''', '''', 7;'';
        EXEC sp_executesql @sqlCommand;
    ', -- Lệnh xóa các file sao lưu cũ hơn 7 ngày
    @database_name = 'Spotify_Group11', -- Database cần liên kết
    @on_success_action = 1, -- Tiếp tục bước tiếp theo
    @on_fail_action = 2; -- Dừng job nếu thất bại
GO

--DIFFERENTIAL BACKUP
-- Tạo Job cho Differential Backup
EXEC sp_add_job 
    @job_name = 'Differential_Backup_Job', --Tên job
    @enabled = 1,  --Bật job
    @description = 'Job to perform Differential Backup every weekday at 00:00';
GO

-- Tạo bước cho Differential Backup
EXEC sp_add_jobstep 
    @job_name = 'Differential_Backup_Job',
    @step_name = 'Differential Backup Step',
    @subsystem = 'TSQL', 
	@command = 'BACKUP DATABASE Spotify_Group11 TO DISK = ''D:\Backup\Spotify_Group11_Diff_'' + CONVERT(NVARCHAR, GETDATE(), 112) + ''_'' + CONVERT(NVARCHAR, GETDATE(), 108) + ''.bak'' WITH DIFFERENTIAL, INIT, FORMAT;',
	@database_name = 'Spotify_Group11',
    @on_success_action = 1, -- Next Step
    @on_fail_action = 2; -- Quit Job
GO

-- Tạo lịch trình cho Differential Backup (Chạy vào các ngày trong tuần lúc 00:00)
EXEC sp_add_schedule 
    @schedule_name = 'Differential_Backup_Schedule',
    @enabled = 1,
    @freq_type = 8, -- Weekly
    @freq_interval = 126, -- Thứ Hai (2) đến Thứ Bảy (62)
	@freq_recurrence_factor = 1,
    @active_start_time = 000000; -- 00:00:00
GO

-- Liên kết Job với Lịch trình
EXEC sp_attach_schedule 
    @job_name = 'Differential_Backup_Job', 
    @schedule_name = 'Differential_Backup_Schedule';
GO

-- Liên kết Job với SQL Server Agent
EXEC sp_add_jobserver 
    @job_name = 'Differential_Backup_Job', 
    @server_name = 'LAPTOP-HFTOHS8V';
GO

--Xóa các bản sao lưu cũ hơn 7 ngày trong Differential Backup Job
EXEC sp_add_jobstep 
    @job_name = 'Differential_Backup_Job',
    @step_name = 'Delete Old Differential Backups',
    @subsystem = 'TSQL', 
    @command = '
        DECLARE @filePath NVARCHAR(255);
        DECLARE @sqlCommand NVARCHAR(MAX);
        
        -- Set backup directory
        SET @filePath = ''D:\Backup\Spotify_Group11_Diff_''; 
        
        -- Xóa các file sao lưu cũ hơn 7 ngày
        SET @sqlCommand = ''EXEC xp_delete_file 0, '''' + @filePath + '''', '''', 7;'';
        EXEC sp_executesql @sqlCommand;
    ',
    @database_name = 'Spotify_Group11',
    @on_success_action = 1, -- Tiếp tục bước tiếp theo
    @on_fail_action = 2; -- Dừng job
GO
--Ghi lại trạng thái backup vào bảng BackupLog để dễ dàng kiểm tra sau này
CREATE TABLE BackupLog (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    BackupType NVARCHAR(50),
    BackupDate DATETIME DEFAULT GETDATE(),
    Status NVARCHAR(50),
    Message NVARCHAR(MAX)
);
-- Với Full backup
EXEC sp_add_jobstep 
    @job_name = 'Full_Backup_Job',
    @step_name = 'Log Full Backup Status',
    @subsystem = 'TSQL',
    @command = '
        BEGIN TRY
            -- Bước sao lưu Full (hoặc các thao tác sao lưu khác)
            -- INSERT INTO BackupLog cho trường hợp thành công
            INSERT INTO BackupLog (BackupType, Status, Message)
            VALUES (''Full Backup'', ''Success'', ''Full Backup completed successfully.'');
        END TRY
        BEGIN CATCH
            -- Bước sao lưu thất bại, ghi lại lỗi vào BackupLog
            INSERT INTO BackupLog (BackupType, Status, Message)
            VALUES (''Full Backup'', ''Fail'', 
                    ''Error occurred during Full Backup: '' + ERROR_MESSAGE());
        END CATCH
    ',
    @on_success_action = 1,
    @on_fail_action = 2;
GO
-- Với Differential backup
EXEC sp_add_jobstep 
    @job_name = 'Differential_Backup_Job',
    @step_name = 'Log Differential Backup Status',
    @subsystem = 'TSQL',
    @command = '
        BEGIN TRY
            -- Bước sao lưu Differential (hoặc các thao tác sao lưu khác)
            -- INSERT INTO BackupLog cho trường hợp thành công
            INSERT INTO BackupLog (BackupType, Status, Message)
            VALUES (''Differential Backup'', ''Success'', ''Differential Backup completed successfully.'');
        END TRY
        BEGIN CATCH
            -- Bước sao lưu thất bại, ghi lại lỗi vào BackupLog
            INSERT INTO BackupLog (BackupType, Status, Message)
            VALUES (''Differential Backup'', ''Fail'', 
                    ''Error occurred during Differential Backup: '' + ERROR_MESSAGE());
        END CATCH
    ',
    @on_success_action = 1,
    @on_fail_action = 2;
GO

