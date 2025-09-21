import Navbar from "components/homepage/Navbar";
import styled from "styled-components";
import { useAuth } from "contexts/AuthContext";
import SectionTabs from "components/common/SectionTabs";

const Wrap = styled.div`
  max-width: 1100px; margin: 40px auto; padding: 0 20px;
`;
const H1 = styled.h1`font-size: 44px; margin-bottom: 8px;`;
const Sub = styled.p`color:#64748b; margin:0 0 24px;`;


export default function Worklist() {
  const { user } = useAuth();
  return (
    <>
    <Navbar />
    <SectionTabs />
      <Wrap>
        <H1>Your worklist, {user?.name || 'User'} 🩺</H1>
        <Sub>Manage your tasks efficiently.</Sub>

      </Wrap>
    </>
  );
}
