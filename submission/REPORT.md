# BÁO CÁO LAB MLOPS

> **Học viên:** Đào Văn Công 
> **Mã học viên:** 2A202600031  
> **Dự án với dữ liệu:** Wine Quality Prediction CI/CD Pipeline  

---

## 1. Kết quả Bước 1: Thực nghiệm với MLflow
Trong giai đoạn thực nghiệm tại máy cục bộ (local), tôi đã tiến hành 16 lần chạy với các tổ hợp siêu tham số khác nhau để tìm ra mô hình tối ưu cho tập dữ liệu Wine Quality.

* **Bộ siêu tham số tối ưu đã chọn:**
    * `n_estimators`: 200
    * `max_depth`: 10
    * `min_samples_split`: 5
* **Kết quả đạt được:** Bộ tham số này mang lại chỉ số Accuracy cao nhất (**0.644**) và F1-score ổn định (**0.642**).

<a href="01_MLflow_Experiments.png">Giao diện so sánh các lần chạy trên MLflow UI</a>

* **Lý do chọn cấu hình này**:
- Độ chính xác cao nhất: Bộ tham số này đạt Accuracy: 0.644, là mức cao nhất trong tất cả các thí nghiệm ở Bước 1.
- Có cân bằng về F1-score (0.642) vì nó rất sát với Accuracy, cho thấy mô hình dự đoán tốt trên cả 3 nhóm chất lượng (thấp, trung bình, cao), không bị thiên kiến (bias) quá mức vào một nhóm chiếm đa số.
- Khả năng hội tụ: So với các lần chạy có n_estimators: 100, việc tăng lên 200 giúp đường biểu diễn độ chính xác mượt hơn và ít biến động khi thay đổi dữ liệu đầu vào.

<a href="01_MLflow_Experiments_2.png">So sánh Parallel Coordinates Plot</a>

---

## 2. Kết quả Bước 2 & 3: Pipeline CI/CD và Huấn luyện liên tục
Toàn bộ quy trình đã được tự động hóa thông qua GitHub Actions, kết nối với Google Cloud Storage (GCS) để quản lý dữ liệu/mô hình và Google Compute Engine (GCE) để phục vụ dự đoán.

### 2.1 So sánh hiệu suất mô hình
Việc bổ sung dữ liệu mới (2998 mẫu) ở Bước 3 đã giúp mô hình cải thiện hiệu suất đáng kể:

| Chỉ số | Bước 2 (2998 mẫu) | Bước 3 (5996 mẫu) |  Chênh lệch  |
| :--- | :---: | :---: |:------------:|
| **Accuracy** | 0.644 | **0.662** |  **+0.018**  |
| **F1 Score** | 0.64168 | **0.65829** | **+0.01661** |

### 2.2 Cấu hình Eval Gate
Để đảm bảo quy trình Deploy không bị gián đoạn nhưng vẫn giữ được tính kiểm định, tôi đã thiết lập ngưỡng Accuracy là **0.60** trong file `mlops.yml`:

```yaml
      - name: Check eval gate
        run: |
          python - <<'EOF'
          import sys
          acc = float("${{ needs.train.outputs.accuracy }}")
          print(f"Accuracy hien tai: {acc}")
          if acc < 0.60:
              print("Accuracy < 0.60. Dung pipeline!")
              sys.exit(1)
          print("Accuracy dat chuan. Chuyen sang Deploy!")
          EOF
```

## 3. Khó khăn kỹ thuật và Giải pháp
Trong quá trình thực hiện Lab, tôi đã gặp và xử lý thành công một số vấn đề kỹ thuật đặc thù:
- Xác thực Google Cloud trong Secret bị lệnh echo xử lý nội dung JSON trực tiếp thường gây lỗi định dạng. **Giải pháp**: dùng mã hóa Base64 để lưu trữ chuỗi Secret và giải mã bằng lệnh base64 -d trong workflow.
- Thao tác lệnh cURL trên Windows: dấu nháy đơn ' không được PowerShell hiểu là chuỗi bao đóng cho dữ liệu JSON. **Giải pháp**: Sử dụng curl.exe kết hợp với dấu nháy kép bao ngoài và thoát nháy nội bộ bằng ký tự backtick (\`).

## 4. Minh chứng triển khai hệ thống
### 4.1 GitHub Actions & Google Cloud Storage
Hệ thống tự động kích hoạt huấn luyện lại ngay khi có commit thay đổi dữ liệu (.dvc).

<a href="02_Github_Actions_Step2_Success.png">Ảnh chạy Bước 2</a>

<a href="03_Github_Actions_Step3_Data_Trigger.png">Ảnh cho thấy chạy tự động nhờ Trigger</a>

<a href="02_GCS_Bucket_Data_Model.png">Minh chứng Google Cloud Storage lưu trữ DVC và Model</a>

### 4.2 API Testing (Health & Predict)
Dịch vụ FastAPI trên VM hoạt động ổn định, trả về kết quả dự đoán chính xác.

<a href="02_Curl_Health_Predict_Step2.png">Ảnh check Health</a>

<a href="02_Curl_Call_Predict_Step2.png">Ảnh check Predict</a>

<a href="03_Curl_Predict_Step3_Result.png">Ảnh check Predict với dữ liệu to hơn</a>

## 5. Kết luận
Dự án đã xây dựng thành công một vòng lặp MLOps khép kín: Dữ liệu mới -> Tự động huấn luyện -> Kiểm tra chất lượng (Eval Gate) -> Triển khai tự động (Deploy). Hệ thống đảm bảo tính tái tạo cao thông qua DVC và khả năng mở rộng linh hoạt trên hạ tầng Cloud.