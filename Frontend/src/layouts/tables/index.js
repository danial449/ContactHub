import { useState, useEffect } from "react";
import axios from "axios";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import DataTable from "examples/Tables/DataTable";
import CircularProgress from "@mui/material/CircularProgress";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import Modal from "@mui/material/Modal";  // Import Modal from MUI
import TextField from "@mui/material/TextField";  // Import TextField
import Box from "@mui/material/Box";  // Import Box for layout

function Tables() {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [openModal, setOpenModal] = useState(false); // State for opening/closing the modal
  const [newContact, setNewContact] = useState({
    first_name: "",
    last_name: "",
    email: "",
    company: "",
    website: "",
    phone: "",
    address: "",
    state: "",
    zip: ""
  });

  useEffect(() => {
    const fetchContacts = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) {
        console.error("No access token found");
        return;
      }

      try {
        const response = await axios.get("http://127.0.0.1:8000/contacts/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setContacts(response.data);
      } catch (error) {
        console.error("Error fetching contacts:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchContacts();
  }, []);

  const columns = [
    { Header: "First Name", accessor: "first_name" },
    { Header: "Last Name", accessor: "last_name" },
    { Header: "Company", accessor: "company" },
    { Header: "Email", accessor: "email" },
    { Header: "Phone", accessor: "phone" },
    { Header: "Address", accessor: "address" },
    { Header: "State", accessor: "state" },
    { Header: "Zip", accessor: "zip" },
    { Header: "Added At", accessor: "added_at" },
    { Header: "Last Modified", accessor: "lastmodifieddate" },
  ];

  const rows = contacts
    .filter((contact) => {
      const query = searchQuery.toLowerCase();
      return (
        contact.first_name.toLowerCase().includes(query) ||
        contact.last_name.toLowerCase().includes(query) ||
        contact.company.toLowerCase().includes(query) ||
        contact.email.toLowerCase().includes(query)
      );
    })
    .map((contact) => ({
      first_name: contact.first_name,
      last_name: contact.last_name,
      company: contact.company,
      email: contact.email,
      phone: contact.phone || "N/A",
      address: contact.address || "N/A",
      state: contact.state || "N/A",
      zip: contact.zip || "N/A",
      added_at: contact.added_at,
      lastmodifieddate: contact.lastmodifieddate,
    }));

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleModalOpen = () => setOpenModal(true); // Open modal
  const handleModalClose = () => setOpenModal(false); // Close modal

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewContact({ ...newContact, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("access_token");
    if (!token) {
      console.error("No access token found");
      return;
    }

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/contacts/",
        newContact,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      console.log("New contact added:", response.data);
      setContacts([...contacts, response.data]); // Add the new contact to the table
      handleModalClose(); // Close the modal
    } catch (error) {
      console.error("Error adding contact:", error);
    }
  };

  if (loading) {
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </MDBox>
    );
  }

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <MDTypography variant="h6" color="white">
                    Contacts Table
                  </MDTypography>
                  <MDButton
                    variant="outlined"
                    size="large"
                    onClick={handleModalOpen}
                  >
                    Add Contact
                  </MDButton>
                  <MDBox pr={1}>
                    <MDInput
                      label="Search here"
                      value={searchQuery}
                      onChange={handleSearchChange}
                      sx={{ label: { color: "#fff" } }}
                    />
                  </MDBox>
                </div>
              </MDBox>

              <MDBox pt={3}>
                <DataTable
                  table={{ columns, rows }}
                  isSorted={false}
                  entriesPerPage={false}
                  showTotalEntries={false}
                  noEndBorder
                />
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>

      <Modal
        open={openModal}
        onClose={handleModalClose}
        aria-labelledby="add-contact-modal"
        aria-describedby="form-to-add-contact"
      >
        <Box sx={{
          width: 500,
          padding: 3,
          backgroundColor: '#fff',
          borderRadius: 2,
          margin: 'auto',
          marginTop: '10%',
          boxShadow: 24
        }}>
          <MDTypography variant="h6" mb={2}>
            Add Contact
          </MDTypography>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="First Name"
                  name="first_name"
                  fullWidth
                  margin="normal"
                  value={newContact.first_name}
                  onChange={handleInputChange}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Last Name"
                  name="last_name"
                  fullWidth
                  margin="normal"
                  value={newContact.last_name}
                  onChange={handleInputChange}
                />
              </Grid>

              {/* Second Row: 2 fields */}
              <Grid item xs={6}>
                <TextField
                  label="Email"
                  name="email"
                  fullWidth
                  margin="normal"
                  value={newContact.email}
                  onChange={handleInputChange}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Company"
                  name="company"
                  fullWidth
                  margin="normal"
                  value={newContact.company}
                  onChange={handleInputChange}
                />
              </Grid>

              {/* Third Row: 2 fields */}
              <Grid item xs={6}>
                <TextField
                  label="Website"
                  name="website"
                  fullWidth
                  margin="normal"
                  value={newContact.website}
                  onChange={handleInputChange}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Phone"
                  name="phone"
                  fullWidth
                  margin="normal"
                  value={newContact.phone}
                  onChange={handleInputChange}
                />
              </Grid>

              {/* Fourth Row: 2 fields */}
              <Grid item xs={6}>
                <TextField
                  label="Address"
                  name="address"
                  fullWidth
                  margin="normal"
                  value={newContact.address}
                  onChange={handleInputChange}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="State"
                  name="state"
                  fullWidth
                  margin="normal"
                  value={newContact.state}
                  onChange={handleInputChange}
                />
              </Grid>

              {/* Fifth Row: 2 fields */}
              <Grid item xs={12}>
                <TextField
                  label="Zip"
                  name="zip"
                  fullWidth
                  margin="normal"
                  value={newContact.zip}
                  onChange={handleInputChange}
                />
              </Grid>
            </Grid>

            <MDButton
              variant="contained"
              color="info"
              fullWidth
              type="submit"
              sx={{ mt: 2 }}
            >
              Add Contact
            </MDButton>
          </form>
        </Box>
      </Modal>
    </DashboardLayout>
  );
}

export default Tables;
