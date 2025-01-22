import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";

// Demo Task React components
import MDBox from "components/MDBox";

// Demo Task React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import reportsLineChartData from "layouts/dashboard/data/reportsLineChartData";
import CircularProgress from "@mui/material/CircularProgress";

// You can use your API call library here like `axios`
import axios from 'axios';

function Dashboard() {
  const [contactsData, setContactsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalContacts, setTotalContacts] = useState(0);
  const [totalCompanies, setTotalCompanies] = useState(0);
  const [contactsAdded, setContactsAdded] = useState(0);
  const [contactsModified, setContactsModified] = useState(0);
  const [addedAtData, setAddedAtData] = useState([]);
  const [modifiedAtData, setModifiedAtData] = useState([]);

  // API call to fetch contacts
  const { sales, tasks } = reportsLineChartData;
  useEffect(() => {

    const fetchContacts = async () => {
      const token = localStorage.getItem("access_token");

      try {
        if (!token) {
          console.error("No access token found");
          return;
        }

        const response = await axios.get('http://127.0.0.1:8000/contacts/', {
          headers: {
            Authorization: `Bearer ${token}`, // Send the token as a Bearer token
          },
        });

        const contacts = response.data;
        setContactsData(contacts);

        // Calculate total contacts
        setTotalContacts(contacts.length);

        // Calculate total unique companies
        const uniqueCompanies = new Set(contacts.map(contact => contact.company));
        setTotalCompanies(uniqueCompanies.size);

        // Count contacts added and modified
        const addedCount = contacts.filter(contact => contact.added_at).length;
        const modifiedCount = contacts.filter(contact => contact.lastmodifieddate).length;
        setContactsAdded(addedCount);
        setContactsModified(modifiedCount);

        // Prepare "added_at" and "modified_at" statistics
        const addedAtCounts = {};
        const modifiedAtCounts = {};

        contacts.forEach(contact => {
          if (contact.added_at) {
            const addedDate = contact.added_at.split("T")[0]; // Get the date part
            addedAtCounts[addedDate] = (addedAtCounts[addedDate] || 0) + 1;
          }

          if (contact.lastmodifieddate) {
            const modifiedDate = contact.lastmodifieddate.split("T")[0];
            modifiedAtCounts[modifiedDate] = (modifiedAtCounts[modifiedDate] || 0) + 1;
          }
        });

        // Convert the added_at and modified_at counts into arrays for charting
        const addedAtDataArr = Object.keys(addedAtCounts).map(date => ({
          date,
          count: addedAtCounts[date]
        }));

        const modifiedAtDataArr = Object.keys(modifiedAtCounts).map(date => ({
          date,
          count: modifiedAtCounts[date]
        }));

        setAddedAtData(addedAtDataArr);
        setModifiedAtData(modifiedAtDataArr);

        setLoading(false);
      } catch (error) {
        console.error("Error fetching contacts data:", error);
        setLoading(false);
      }
    };

    fetchContacts();
  }, []);

  if (loading) {
    return <MDBox display="flex" justifyContent="center" alignItems="center" height="100vh">
    <CircularProgress />
  </MDBox> // You can replace this with a spinner or loader component
  }

  return (
    <DashboardLayout>
      <DashboardNavbar />

      <MDBox py={3}>
        <Grid container spacing={3}>
          {/* Total Contacts */}
          <Grid item xs={12} md={6} lg={6}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="contacts"
                title="Total Contacts"
                count={totalContacts}
              />
            </MDBox>
          </Grid>

          {/* Total Companies */}
          <Grid item xs={12} md={6} lg={6}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="business"
                title="Total Companies"
                count={totalCompanies}
              />
            </MDBox>
          </Grid>

          {/* Contacts Added */}
         
        </Grid>

        {/* Charts for Contacts Added and Contacts Modified */}
        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            {/* Added at chart */}
            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                <ReportsLineChart
                  color="info"
                  title="Contacts Added"
                  description="Contacts added over time"
                  date="updated recently"
                  chart={tasks}
                />
              </MDBox>
            </Grid>

            {/* Modified at chart */}
            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                <ReportsLineChart
                  color="success"
                  title="Contacts Modified"
                  description="Contacts modified over time"
                  date="updated recently"
                  chart={sales}
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>

    </DashboardLayout>
  );
}

export default Dashboard;
