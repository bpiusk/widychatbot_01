import {
  Box, Button, Input, Text, VStack, Heading, Flex
} from "@chakra-ui/react";
import React, { useState } from "react";
import { adminLogin } from "../api";

export default function AdminLogin({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await adminLogin(username, password);
      if (res.access_token) {
        onLogin(res.access_token);
      } else {
        setError("Username atau password salah.");
      }
    } catch {
      setError("Gagal login. Silakan coba lagi.");
    }
    setLoading(false);
  };

  return (
    <Flex minH="100vh" align="center" justify="center" bg="background.100">
      <Box
        p={8}
        borderRadius="xl"
        boxShadow="lg"
        bg="white"
        minW="320px"
        border="1px solid"
        borderColor="primary.500"
      >
        <Heading mb={6} color="primary.500" size="lg" textAlign="center">
          Admin Login
        </Heading>
        <VStack spacing={4}>
          <Input
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            bg="background.100"
            borderColor="primary.500"
            color="text.900"
          />
          <Input
            placeholder="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            bg="background.100"
            borderColor="primary.500"
            color="text.900"
          />
          {error && <Text color="red.500">{error}</Text>}
          <Button
            colorScheme="primary"
            bg="primary.500"
            color="white"
            _hover={{ bg: "accent.500" }}
            isLoading={loading}
            onClick={handleLogin}
            w="100%"
          >
            Login
          </Button>
        </VStack>
      </Box>
    </Flex>
  );
}