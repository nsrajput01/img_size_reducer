const imageInput = document.getElementById("imageInput");

const preview = document.getElementById("preview");

const fileName = document.getElementById("fileName");

const imageInfo = document.getElementById("imageInfo");

const name = document.getElementById("name");

const originalSize = document.getElementById("originalSize");

const dimensions = document.getElementById("dimensions");

const compressBtn = document.getElementById("compressBtn");

const targetSize = document.getElementById("targetSize");

const sizeUnit = document.getElementById("sizeUnit");

const result = document.getElementById("result");

const resultOriginal = document.getElementById("resultOriginal");

const resultCompressed = document.getElementById("resultCompressed");

const reduction = document.getElementById("reduction");

const downloadBtn = document.getElementById("downloadBtn");


let selectedFile = null;


// -----------------------------
// File selection
// -----------------------------

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) {
        return;
    }

    selectedFile = file;

    fileName.textContent = file.name;

    name.textContent = file.name;


    // Original size

    const sizeKB = file.size / 1024;

    if (sizeKB >= 1024) {

        originalSize.textContent =
            (sizeKB / 1024).toFixed(2) + " MB";

    } else {

        originalSize.textContent =
            sizeKB.toFixed(2) + " KB";
    }


    // Preview

    const reader = new FileReader();

    reader.onload = function (event) {

        preview.src = event.target.result;

        imageInfo.style.display = "flex";


        const img = new Image();

        img.onload = function () {

            dimensions.textContent =
                img.width + " × " +
                img.height + " px";

        };

        img.src = event.target.result;

    };

    reader.readAsDataURL(file);

});


// -----------------------------
// Compression
// -----------------------------

compressBtn.addEventListener("click", async function () {

    if (!selectedFile) {

        alert("Please select an image first.");

        return;
    }


    if (!targetSize.value || targetSize.value <= 0) {

        alert("Please enter a target size.");

        return;
    }


    // Button loading state

    compressBtn.disabled = true;

    compressBtn.textContent = "Compressing...";


    const formData = new FormData();

    formData.append("image", selectedFile);

    formData.append("targetSize", targetSize.value);

    formData.append("unit", sizeUnit.value);


    try {

        const response = await fetch("/compress", {

            method: "POST",

            body: formData

        });


        const data = await response.json();


        if (!data.success) {

            alert(data.message);

            return;
        }


        // Show result

        result.style.display = "block";


        resultOriginal.textContent =
            formatSize(data.originalSize);


        resultCompressed.textContent =
            formatSize(data.compressedSize);


        reduction.textContent =
            data.reduction + "%";


        // Download button

        downloadBtn.onclick = function () {

            window.location.href =
                data.downloadUrl;

        };


    } catch (error) {

        console.error(error);

        alert("Something went wrong.");

    } finally {

        compressBtn.disabled = false;

        compressBtn.textContent =
            "Compress Image";

    }

});


// -----------------------------
// Format file size
// -----------------------------

function formatSize(bytes) {

    if (bytes >= 1024 * 1024) {

        return (
            bytes / (1024 * 1024)
        ).toFixed(2) + " MB";

    }

    return (
        bytes / 1024
    ).toFixed(2) + " KB";
}