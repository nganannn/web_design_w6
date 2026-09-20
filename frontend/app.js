const API_URL = "http://127.0.0.1:8000/items";

const form = document.getElementById("item-form");
const nameInput = document.getElementById("name");
const priceInput = document.getElementById("price");
const tableBody = document.getElementById("item-table-body");
const cancelBtn = document.getElementById("cancel-btn");

async function fetchItems() {
  try {
    const response = await fetch(API_URL);
    const items = await response.json();

    tableBody.innerHTML = "";

    items.forEach((item) => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${item.id}</td>
        <td>${item.name}</td>
        <td>${item.price}</td>
        <td>
          <button class="delete-btn" data-id="${item.id}">Delete</button>
        </td>
      `;

      tableBody.appendChild(row);
    });

    bindDeleteButtons();
  } catch (error) {
    console.error("Fetch failed:", error);
    alert("Không thể tải dữ liệu từ backend");
  }
}

async function addItem(event) {
  event.preventDefault();

  const name = nameInput.value.trim();
  const price = Number(priceInput.value);

  if (!name || Number.isNaN(price)) {
    alert("Vui lòng nhập tên và giá hợp lệ");
    return;
  }

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, price }),
    });

    if (!response.ok) {
      throw new Error("Add item failed");
    }

    form.reset();
    fetchItems();
  } catch (error) {
    console.error("Add error:", error);
    alert("Thêm dữ liệu thất bại");
  }
}

async function deleteItem(id) {
  try {
    const response = await fetch(`${API_URL}/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error("Delete failed");
    }

    fetchItems();
  } catch (error) {
    console.error("Delete error:", error);
    alert("Xóa dữ liệu thất bại");
  }
}

function bindDeleteButtons() {
  document.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.id;
      deleteItem(id);
    });
  });
}

form.addEventListener("submit", addItem);
cancelBtn.addEventListener("click", () => form.reset());

fetchItems();