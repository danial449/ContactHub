import React from "react";
import PropTypes from "prop-types"; // Import PropTypes
import { Navigate } from "react-router-dom";

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("access_token");

  // If the user is not authenticated (no token), redirect to login page
  if (!token) {
    return <Navigate to="/authentication/sign-in" />;
  }

  // If the user is authenticated, render the child components (protected route)
  return children;
};

// Define PropTypes for the component
PrivateRoute.propTypes = {
  children: PropTypes.node.isRequired, // Specify that 'children' should be a node and is required
};

export default PrivateRoute;
