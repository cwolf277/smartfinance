import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

jest.mock("./services/api", () => ({
  __esModule: true,
  default: {
    getStoredTransactions: () => Promise.resolve({ transactions: [] }),
    createLinkToken: () => Promise.resolve({ link_token: "test" }),
  },
}));

jest.mock("react-plaid-link", () => ({
  usePlaidLink: () => ({ open: jest.fn(), ready: false }),
}));

jest.mock("react-chartjs-2", () => ({
  Bar: () => null,
}));

test("renders SmartFinance brand", () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );
  expect(screen.getByText(/SmartFinance/i)).toBeInTheDocument();
});
