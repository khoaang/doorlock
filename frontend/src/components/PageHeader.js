import React from "react";
import { Box, Typography, Breadcrumbs, Link } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

const PageHeader = ({ title, breadcrumbs = [], action, description }) => {
  return (
    <Box mb={4}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={1}
      >
        <Box>
          {breadcrumbs.length > 0 && (
            <Breadcrumbs sx={{ mb: 1 }}>
              {breadcrumbs.map((crumb, index) => {
                const isLast = index === breadcrumbs.length - 1;
                return isLast ? (
                  <Typography key={crumb.text} color="text.primary">
                    {crumb.text}
                  </Typography>
                ) : (
                  <Link
                    key={crumb.text}
                    component={RouterLink}
                    to={crumb.href}
                    underline="hover"
                    color="inherit"
                  >
                    {crumb.text}
                  </Link>
                );
              })}
            </Breadcrumbs>
          )}
          <Typography variant="h4" component="h1" gutterBottom>
            {title}
          </Typography>
          {description && (
            <Typography variant="body1" color="text.secondary">
              {description}
            </Typography>
          )}
        </Box>
        {action && <Box>{action}</Box>}
      </Box>
    </Box>
  );
};

export default PageHeader;
