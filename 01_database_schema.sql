--TẠO BẢN SAO CHO TỪNG BẢNG DỮ LIỆU GỐC
INSERT INTO [dbo].[artists ] SELECT * FROM [dbo].[artists_original];
INSERT INTO [dbo].[playlists] SELECT * FROM [dbo].[playlists_original];
INSERT INTO [dbo].[tracks] SELECT * FROM [dbo].[tracks_original];
INSERT INTO [dbo].[audio_features] SELECT * FROM [dbo].[audio_features_original];

-- THỦ TỤC XÓA TRÙNG LẶP TRONG BẢNG tracks
CREATE PROCEDURE RemoveDuplicateTracks
AS
BEGIN
    -- Bắt đầu giao dịch
    BEGIN TRANSACTION;

    -- Sử dụng CTE để tìm các bản ghi trùng lặp
    WITH CTE_Duplicates AS (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY track_id ORDER BY (SELECT NULL)) AS row_num
        FROM 
            tracks
    )
    -- Xóa các bản ghi trùng lặp, chỉ giữ lại bản ghi đầu tiên (row_num = 1)
    DELETE FROM CTE_Duplicates 
    WHERE row_num > 1;

    -- Cam kết giao dịch
    COMMIT TRANSACTION;
END;
-- GỌI THỦ TỤC
exec  RemoveDuplicateTracks;

-- THỦ TỤC XÓA BẢN GHI TRÙNG LẶP TRONG BẢNG Artists
CREATE PROCEDURE RemoveDuplicateArtists
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH CTE AS (
        SELECT 
            id,
            ROW_NUMBER() OVER (PARTITION BY id ORDER BY (SELECT NULL)) AS row_num
        FROM 
            artists
    )
    DELETE FROM CTE WHERE row_num > 1;
END;
-- GỌI THỦ TỤC
exec RemoveDuplicateArtists;
-- THỦ TỤC TÁCH CỘT artist_names và artist_ids trong bảng tracks từ dạng list sang các giá trị độc lập và lưu vào bảng trung gian ArtistData 
CREATE PROCEDURE SplitArtistData
AS
BEGIN
    -- Tạo bảng tạm để lưu trữ kết quả
    CREATE TABLE ArtistData (
        TrackID NVARCHAR(50),  -- Thêm cột TrackID
        ArtistID NVARCHAR(50),
        ArtistName NVARCHAR(MAX)
    );

    -- Tách và chèn dữ liệu vào bảng tạm
    INSERT INTO ArtistData (TrackID, ArtistID, ArtistName)
    SELECT 
        t.track_id,  -- Chọn track_id từ bảng tracks_sp
        TRIM(ids.value) AS ArtistID,  
        TRIM(names.value) AS ArtistName
    FROM tracks t
    CROSS APPLY (
        SELECT value
        FROM STRING_SPLIT(REPLACE(REPLACE(t.artist_ids, '[', ''), ']', ''), ',')
    ) AS ids
    CROSS APPLY (
        SELECT value
        FROM STRING_SPLIT(REPLACE(REPLACE(t.artist_names, '[', ''), ']', ''), ',')
    ) AS names;

    -- Trả về kết quả, không có dấu nháy đơn
    SELECT 
        TrackID, 
        ArtistID, 
        ArtistName 
    FROM ArtistData;
END;
-- GỌI THỦ TỤC
exec SplitArtistData;
--- THỦ TỤC XÓA CÁC BẢN GHI TRÙNG TRONG BẢNG ArtistData
CREATE PROCEDURE DeleteDuplicateArtistsData
AS
BEGIN
    -- Xóa các bản ghi trùng lặp, giữ lại bản ghi đầu tiên
    WITH CTE_Duplicates AS (
        SELECT 
            TrackID,
            ArtistID,
            ArtistName,
            ROW_NUMBER() OVER (PARTITION BY ArtistID, ArtistName ORDER BY TrackID) AS RowNum
        FROM 
            dbo.ArtistData
    )
    DELETE FROM CTE_Duplicates
    WHERE RowNum > 1;  -- Xóa các bản ghi có RowNum lớn hơn 1 (trùng lặp)
END;
exec DeleteDuplicateArtistsData;


-- THỦ TỤC PHÂN LOẠI ĐỘ NỔI TIẾNG CỦA NGHỆ SĨ
-- TẠO THÊM CỘT Popularity_level trong bảng artists
ALTER TABLE artists
ADD Popularity_level VARCHAR(20);
-- TẠO THỦ TỤC
CREATE PROCEDURE ClassifyArtistPopularity
AS
BEGIN
    UPDATE artists
    SET 
        Popularity_level = CASE
            WHEN popularity >= 0 AND popularity < 20 THEN 'Very Low'
            WHEN popularity >= 20 AND popularity < 50 THEN 'Low'
            WHEN popularity >= 50 AND popularity < 70 THEN 'Medium'
            WHEN popularity >= 70 AND popularity < 90 THEN 'High'
            WHEN popularity >= 90 AND popularity <= 100 THEN 'Very High'
            ELSE 'Unknown' -- Xử lý trường hợp không nằm trong phạm vi
        END;
END;
-- GỌI THỦ TỤC
EXEC ClassifyArtistPopularity ;

-- TẠO KHÓA NGOẠI CHO CƠ SỞ DỮ LIỆU
-- TẠO QUAN HỆ GIỮA BẢNG tracks và bảng playlist
alter table [dbo].[tracks]
add constraint FK_tracks
foreign key ([playlist_id]) references [dbo].[playlists]([playlist_id]);
-- tạo quan hệ giữa bảng audio_features và bảng tracks
alter table [dbo].[audio_features]
add constraint FK_FeaturesS
foreign key ([id]) references [dbo].[tracks]([track_id]);
-- tạo quan hệ giữa bảng ArtistData và bảng tracks, artists
alter table [dbo].[ArtistData]
ADD CONSTRAINT FK_Artists
FOREIGN KEY ([TrackID]) REFERENCES [dbo].[tracks]([track_id]) ON DELETE CASCADE,
FOREIGN KEY ([ArtistID]) REFERENCES [dbo].[artists]([id]) ON DELETE CASCADE;

--- THỦ TỤC THAY THẾ GIÁ TRỊ NULL TRONG CỘT DESCRIPTION THÀNH UNKNOWN
CREATE PROCEDURE UpdatePlaylistDescriptions
AS
BEGIN
    -- Cập nhật các giá trị description NULL thành 'unknown'
    UPDATE playlists
    SET description = 'unknown'
    WHERE description IS NULL;
END;
-- gọi thủ tục
EXEC UpdatePlaylistDescriptions;

-- HÀM CHUYỂN ĐỔI CỘT track_duration_ms trong bảng tracks từ mili giây sang phút
-- thêm cột mới trong bảng để lưu giá trị chuyển đổi
ALTER TABLE [dbo].[tracks]
ADD duration_minutes DECIMAL(10, 2); 
-- viết hàm chuyển đổi
CREATE FUNCTION dbo.ConvertMsToMinutes
(
    @track_duration_ms INT
)
RETURNS DECIMAL(10, 2)
AS
BEGIN
    RETURN ROUND(@track_duration_ms / 60000.0, 2);  -- Chia cho 60.000 và làm tròn đến 2 chữ số thập phân
END;
-- cập nhật cột mới
UPDATE [dbo].[tracks]
SET duration_minutes = dbo.ConvertMsToMinutes(track_duration_ms);
