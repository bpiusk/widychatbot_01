import React, { useState } from "react";
import { chat } from "../api";
import {
  Box,
  Button,
  Flex,
  Input,
  Text,
  VStack,
  HStack,
  useColorModeValue,
  Spinner,
} from "@chakra-ui/react";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { from: "user", text: input }]);
    setLoading(true);
    try {
      const res = await chat(input);
      setMessages((prev) => [...prev, { from: "bot", text: res.answer }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "Terjadi kesalahan. Coba lagi." },
      ]);
    }
    setInput("");
    setLoading(false);
  };

  return (
    <Box
      maxW="600px"
      w="100%"
      mx="auto"
      mt={10}
      p={6}
      borderRadius="xl"
      boxShadow="lg"
      bg="background.100"
      border="1px solid"
      borderColor="primary.500"
    >
      <Text fontSize="2xl" fontWeight="bold" color="primary.500" mb={4}>
        WidyChatbot
      </Text>
      <VStack
        align="stretch"
        spacing={3}
        minH="300px"
        bg="white"
        borderRadius="md"
        p={3}
        mb={4}
        boxShadow="sm"
      >
        {messages.map((msg, idx) => (
          <Flex
            key={idx}
            justify={msg.from === "user" ? "flex-end" : "flex-start"}
          >
            <Box
              bg={msg.from === "user" ? "secondary.500" : "primary.500"}
              color="white"
              borderRadius="2xl"
              px={4}
              py={2}
              maxW="80%"
              wordBreak="break-word"
              fontSize="md"
            >
              {msg.text}
            </Box>
          </Flex>
        ))}
        {loading && (
          <Flex>
            <Spinner size="sm" mr={2} color="primary.500" />
            <Text color="text.700">Mengetik...</Text>
          </Flex>
        )}
      </VStack>
      <form onSubmit={handleSend}>
        <Flex gap={2}>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tanyakan sesuatu tentang kampus..."
            isDisabled={loading}
            flex={1}
            bg="white"
            borderColor="primary.500"
            color="text.900"
          />
          <Button
            type="submit"
            colorScheme="primary"
            bg="primary.500"
            color="white"
            _hover={{ bg: "accent.500" }}
            isDisabled={loading || !input.trim()}
          >
            Kirim
          </Button>
        </Flex>
      </form>
    </Box>
  );
}